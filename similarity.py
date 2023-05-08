
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Union
import cityDetails
import categorize
from models import Cases, session, Recommendation
import ml
from sklearn.ensemble import RandomForestClassifier


class Case(BaseModel):
    start_date: str
    end_date: str
    city: str
    problem_start_number_of_active_cases: int
    problem_end_number_of_active_cases: int
    problem_start_number_of_icu_active_cases: int
    problem_end_number_of_icu_active_cases: int
    problem_start_number_of_deaths: int
    problem_end_number_of_deaths: int
    problem_vaccinated_population: int
    problem_average_temperature: float
    problem_average_humidity: float
    solution_lockdown_policy_level: int
    solution_mask_policy_level: int
    solution_vaccine_policy_level: int


class CaseRecommendation(BaseModel):
    start_date: str
    end_date: str | None = None
    city: str
    problem_start_number_of_active_cases: int
    problem_end_number_of_active_cases: Union[int, str] | None = None
    problem_start_number_of_icu_active_cases: int
    problem_end_number_of_icu_active_cases: Union[int, str] | None = None
    problem_start_number_of_deaths: int
    problem_end_number_of_deaths: Union[int, str] | None = None
    problem_vaccinated_population: Union[int, str] | None = None
    problem_average_temperature: Union[float, str] | None = None
    problem_average_humidity: Union[float, str] | None = None


router = APIRouter()


def get_cases():
    all_cases = []
    cases_query = session.query(Cases)
    for i in cases_query.all():
        all_cases.append(i.__dict__)
    return all_cases


@router.get("/recommendation")
async def get_all_recommendation():
    recommendation_query = session.query(Recommendation)
    return ({"result": recommendation_query.all()})


@router.post("/recommendation")
def recommendation(case: CaseRecommendation):
    if len(get_cases()) < 4:
        return ({"result": "Not enough cases. At least 4 cases are rquired."})
    city_details = cityDetails.cities[case.city]

    infection_rate = round((case.problem_start_number_of_active_cases /
                            city_details["population"]) * 100, 2)
    mortality_rate = round((case.problem_start_number_of_deaths /
                            city_details["population"]) * 100, 2)
    # age_distribution, age_category = categorize.categorize_age(city_details["median_age"])
    density_distribution, density_category = categorize.categorize_density(
        city_details["density"], city_details["population"])

    p_description = f'Currently, the population density in this area is **{density_category}**. The total population in the affected area is **{city_details["population"]}**, and it has a **{city_details["median_age"]}** median age distribution. There are currently **{case.problem_start_number_of_active_cases}** active cases of the disease in the area, out of which **{case.problem_start_number_of_icu_active_cases}** are severe cases. **{case.problem_start_number_of_deaths}** deaths have also been reported so far. The infection rate in this area is **{infection_rate} percentage** and the mortality rate is **{mortality_rate} percentage**.'

    new_problem = case.__dict__
    new_problem['problem_population'] = city_details['population']
    new_problem['problem_population_density'] = density_distribution
    new_problem['problem_age_distribution'] = city_details["median_age"]
    new_problem['problem_mortality_rate'] = mortality_rate
    new_problem['problem_infection_rate'] = infection_rate

    # similarity comparision for features than are not null
    numerical_features = []
    for key, value in new_problem.items():
        if value != "" and key != "start_date" and key != "end_date" and key != "city":
            numerical_features.append(key)

    all_similar_date = ml.find_similar_cases_by_distance(
        new_problem, get_cases(), numerical_features, 4, 'euclidean')
    # all_similar_date = similarity.similar_cases_knn(new_problem, get_cases())
    similar_data = all_similar_date[0]
    lockdown_policy_description, lockdown_level = categorize.lockdown_policy(categorize.lockdown_policy_evaluation(case.problem_vaccinated_population,case.problem_start_number_of_active_cases,city_details["population"]))
    print(lockdown_level)
    # lockdown_policy_description = categorize.lockdown_policy(
    #     similar_data['solution_lockdown_policy_level'])
    mask_policy_description = categorize.mask_policy(
        similar_data['solution_mask_policy_level'])

    if case.problem_vaccinated_population == 0:
        vaccine_policy_description = categorize.vaccine_policy(case.problem_vaccinated_population)
    elif similar_data['solution_vaccine_policy_level'] < case.problem_vaccinated_population:
        vaccine_policy_description = categorize.vaccine_policy(case.problem_vaccinated_population)
    else:
        vaccine_policy_description = categorize.vaccine_policy(
        similar_data['solution_vaccine_policy_level'])

    solution_description_template = f'In a scenario where the population density is **{density_category}**, medain age is **{city_details["median_age"]}**, infection rate is **{infection_rate}** percentage, and mortality rate is **{mortality_rate} percentage**, **with {case.problem_start_number_of_icu_active_cases}** icu active cases.  \nIt is recommended to implement a **level {lockdown_level} lockdown policy**, {lockdown_policy_description}.  \nA **level {similar_data["solution_mask_policy_level"]} mask policy** {mask_policy_description}.  \nIt is important to note that {vaccine_policy_description}.  \nOverall, taking these measures can help control the spread of the disease and minimize the number of severe cases and deaths in the affected area.'
    similar_solution = []
    for x in all_similar_date[1:]:
        similar_solution.append(x["solution_description"])

    caseAdd = Recommendation(start_date=case.start_date,
                             end_date=None if case.end_date == "" else case.end_date,
                             city=case.city,
                             problem_description=p_description,
                             problem_population_density=density_distribution,
                             problem_population=city_details["population"],
                             problem_age_distribution=city_details["median_age"],
                             problem_start_number_of_active_cases=case.problem_start_number_of_active_cases,
                             problem_end_number_of_active_cases=None if case.problem_end_number_of_active_cases == "" else case.problem_end_number_of_active_cases,
                             problem_start_number_of_icu_active_cases=case.problem_start_number_of_icu_active_cases,
                             problem_end_number_of_icu_active_cases=None if case.problem_end_number_of_icu_active_cases == "" else case.problem_end_number_of_icu_active_cases,
                             problem_start_number_of_deaths=case.problem_start_number_of_deaths,
                             problem_end_number_of_deaths=None if case.problem_end_number_of_deaths == "" else case.problem_end_number_of_deaths,
                             problem_vaccinated_population=None if case.problem_vaccinated_population == "" else case.problem_vaccinated_population,
                             problem_infection_rate=infection_rate,
                             problem_mortality_rate=mortality_rate,
                             problem_average_temperature=None if case.problem_average_temperature == "" else case.problem_vaccinated_population,
                             problem_average_humidity=None if case.problem_average_humidity == "" else case.problem_average_humidity,
                             solution_description=solution_description_template,
                             solution_lockdown_policy_level=lockdown_level,
                             solution_mask_policy_level=similar_data['solution_mask_policy_level'],
                             solution_vaccine_policy_level=similar_data['solution_vaccine_policy_level'])

    session.add(caseAdd)
    session.commit()
    cases_query = session.query(Recommendation)
    return ({"recommendation": solution_description_template,
             "most_similar": [
                similar_solution
             ]})


@router.delete("/recommendation/{id}")
async def delete_recommendation(id: int):
    case = session.query(Recommendation).filter(
        Recommendation.id == id).first()
    session.delete(case)
    session.commit()
    return {"Recommendation deleted": case.id}


@router.post("/recommendation/knn")
async def recommendation_knn(case: CaseRecommendation):
    if len(get_cases()) < 4:
        return ({"result": "Not enough cases. At least 4 cases are rquired."})
    city_details = cityDetails.cities[case.city]

    infection_rate = round((case.problem_start_number_of_active_cases /
                            city_details["population"]) * 100, 2)
    mortality_rate = round((case.problem_start_number_of_deaths /
                            city_details["population"]) * 100, 2)

    density_distribution, density_category = categorize.categorize_density(
        city_details["density"], city_details["population"])

    new_problem = case.__dict__
    new_problem['problem_population'] = city_details['population']
    new_problem['problem_population_density'] = density_distribution
    new_problem['problem_age_distribution'] = city_details["median_age"]
    new_problem['problem_mortality_rate'] = mortality_rate
    new_problem['problem_infection_rate'] = infection_rate

    # similarity comparision for features than are not null
    numerical_features = []
    for key, value in new_problem.items():
        if value != "" and key != "start_date" and key != "end_date" and key != "city":
            numerical_features.append(key)

    all_similar_date = ml.similar_cases_knn(
        new_problem, get_cases(), numerical_features)

    similar_data = all_similar_date
    solution_description_template = add_recommendation(case,similar_data)

    return ({"recommendation": solution_description_template})


@router.post("/recommendation/decision_tree")
async def recommendation_decision_tree(case: CaseRecommendation):
    if len(get_cases()) < 4:
        return ({"result": "Not enough cases. At least 4 cases are rquired."})
    city_details = cityDetails.cities[case.city]

    infection_rate = round((case.problem_start_number_of_active_cases /
                            city_details["population"]) * 100, 2)
    mortality_rate = round((case.problem_start_number_of_deaths /
                            city_details["population"]) * 100, 2)
    density_distribution, density_category = categorize.categorize_density(
        city_details["density"], city_details["population"])

    new_problem = case.__dict__
    new_problem['problem_population'] = city_details['population']
    new_problem['problem_population_density'] = density_distribution
    new_problem['problem_age_distribution'] = city_details["median_age"]
    new_problem['problem_mortality_rate'] = mortality_rate
    new_problem['problem_infection_rate'] = infection_rate

    # similarity comparision for features than are not null
    numerical_features = []
    for key, value in new_problem.items():
        if value != "" and key != "start_date" and key != "end_date" and key != "city":
            numerical_features.append(key)

    all_similar_date = ml.similar_cases_decison_tree(
        new_problem, get_cases(), numerical_features)

    similar_data = all_similar_date
    solution_description_template = add_recommendation(case,similar_data)

    return ({"recommendation": solution_description_template})


@router.get("/evaluation")
async def evaluation_of_algorithms():
    result = ml.calculate_metrices(get_cases())
    return ({"result": result})


def add_recommendation(case,similar_data):

    city_details = cityDetails.cities[case.city]

    infection_rate = round((case.problem_start_number_of_active_cases /
                            city_details["population"]) * 100, 2)
    mortality_rate = round((case.problem_start_number_of_deaths /
                            city_details["population"]) * 100, 2)
    # age_distribution, age_category = categorize.categorize_age(city_details["median_age"])
    density_distribution, density_category = categorize.categorize_density(
        city_details["density"], city_details["population"])

    p_description = f'Currently, the population density in this area is **{density_category}**. The total population in the affected area is **{city_details["population"]}**, and it has a **{city_details["median_age"]}** median age distribution. There are currently **{case.problem_start_number_of_active_cases}** active cases of the disease in the area, out of which **{case.problem_start_number_of_icu_active_cases}** are severe cases. **{case.problem_start_number_of_deaths}** deaths have also been reported so far. The infection rate in this area is **{infection_rate} percentage** and the mortality rate is **{mortality_rate} percentage**.'

    lockdown_policy_description = categorize.lockdown_policy(
        similar_data['solution_lockdown_policy_level'][0])
    mask_policy_description = categorize.mask_policy(
        similar_data['solution_mask_policy_level'][0])
    vaccine_policy_description = categorize.vaccine_policy(
        similar_data['solution_vaccine_policy_level'][0])

    solution_description_template = f'In a scenario where the population density is **{density_category}**, medain age is **{city_details["median_age"]}**, infection rate is **{infection_rate}** percentage, and mortality rate is **{mortality_rate} percentage**, **with {case.problem_start_number_of_icu_active_cases}** icu active cases.  \nIt is recommended to implement a **level {similar_data["solution_lockdown_policy_level"][0]} lockdown policy**, {lockdown_policy_description}.  \nA **level {similar_data["solution_mask_policy_level"][0]} mask policy** {mask_policy_description}.  \nIt is important to note that {vaccine_policy_description}.  \nOverall, taking these measures can help control the spread of the disease and minimize the number of severe cases and deaths in the affected area.'

    caseAdd = Recommendation(start_date=case.start_date,
                             end_date=None if case.end_date == "" else case.end_date,
                             city=case.city,
                             problem_description=p_description,
                             problem_population_density=density_distribution,
                             problem_population=city_details["population"],
                             problem_age_distribution=city_details["median_age"],
                             problem_start_number_of_active_cases=case.problem_start_number_of_active_cases,
                             problem_end_number_of_active_cases=None if case.problem_end_number_of_active_cases == "" else case.problem_end_number_of_active_cases,
                             problem_start_number_of_icu_active_cases=case.problem_start_number_of_icu_active_cases,
                             problem_end_number_of_icu_active_cases=None if case.problem_end_number_of_icu_active_cases == "" else case.problem_end_number_of_icu_active_cases,
                             problem_start_number_of_deaths=case.problem_start_number_of_deaths,
                             problem_end_number_of_deaths=None if case.problem_end_number_of_deaths == "" else case.problem_end_number_of_deaths,
                             problem_vaccinated_population=None if case.problem_vaccinated_population == "" else case.problem_vaccinated_population,
                             problem_infection_rate=infection_rate,
                             problem_mortality_rate=mortality_rate,
                             problem_average_temperature=None if case.problem_average_temperature == "" else case.problem_vaccinated_population,
                             problem_average_humidity=None if case.problem_average_humidity == "" else case.problem_average_humidity,
                             solution_description=solution_description_template,
                             solution_lockdown_policy_level=int(
                                 similar_data['solution_lockdown_policy_level'][0]),
                             solution_mask_policy_level=int(
                                 similar_data['solution_mask_policy_level'][0]),
                             solution_vaccine_policy_level=int(similar_data['solution_vaccine_policy_level'][0]))

    session.add(caseAdd)
    try:
        session.commit()
    except:
        session.rollback()
        raise
    return solution_description_template
