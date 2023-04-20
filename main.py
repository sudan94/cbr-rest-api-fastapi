from fastapi import FastAPI
from models import Cases, session, Recommendation
from pydantic import BaseModel
import cityDetails
from fastapi.middleware.cors import CORSMiddleware
import categorize
import similarity
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
    problem_average_temprature: float
    problem_average_humidity: float
    solution_lockdown_policy_level: int
    solution_mask_policy_level: int
    solution_vaccine_policy_level: int
class CaseRecommendation(BaseModel):
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
    problem_average_temprature: float
    problem_average_humidity: float

app = FastAPI()
origins = [
    "http://localhost:3000",
    "https://cbr-covid.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/cases")
async def get_all_cases():
    cases_query = session.query(Cases)
    return ({"data": cases_query.all()})

def get_cases():
    all_cases = []
    cases_query = session.query(Cases)
    for i in cases_query.all():
        all_cases.append(i.__dict__)
    return all_cases

@app.post("/cases/create")
async def create_case(case: Case):

    city_details = cityDetails.cities[case.city]
    infection_rate = round((case.problem_start_number_of_active_cases /
                            city_details["population"]) * 100, 2)
    mortality_rate = round((case.problem_start_number_of_deaths /
                            city_details["population"]) * 100, 2)
    age_distribution, age_category = categorize.categorize_age(city_details["median_age"])
    density_distribution, density_category = categorize.categorize_density(
        city_details["median_age"], city_details["population"])
    effectivness = categorize.claculate_effectivness(case.problem_start_number_of_active_cases, case.problem_end_number_of_active_cases,
                                          case.problem_start_number_of_icu_active_cases, case.problem_end_number_of_icu_active_cases)

    lockdown_policy_description = categorize.lockdown_policy(
        case.solution_lockdown_policy_level)
    mask_policy_description = categorize.mask_policy(case.solution_mask_policy_level)
    vaccine_policy_description = categorize.vaccine_policy(
        case.solution_vaccine_policy_level)

    p_description = f'Currently, the population density in this area is **{density_category}**. The total population in the affected area is **{city_details["population"]}**, and it has a **{age_category}** age distribution. There are currently **{case.problem_start_number_of_active_cases}** active cases of the disease in the area, out of which **{case.problem_start_number_of_icu_active_cases}** are severe cases. **{case.problem_start_number_of_deaths}** deaths have also been reported so far. The infection rate in this area is **{infection_rate} percentage** and the mortality rate is **{mortality_rate} percentage**.'

    solution_description_template = f'In a scenario where the population density is **{density_category}**, age distribution is **{age_category}**, infection rate is **{infection_rate}** percentage, and mortality rate is **{mortality_rate} percentage**, **with {case.problem_start_number_of_icu_active_cases}** icu active cases. </br> </br> It is recommended to implement a **level {case.solution_lockdown_policy_level} lockdown policy**, {lockdown_policy_description}.</br> A **level {case.solution_mask_policy_level} mask policy** {mask_policy_description}.</br> It is important to note that {vaccine_policy_description}.</br> Overall, taking these measures can help control the spread of the disease and minimize the number of severe cases and deaths in the affected area.'

    caseAdd = Cases(start_date=case.start_date,
                    end_date=case.end_date,
                    city=case.city,
                    problem_description=p_description,
                    problem_population_density=density_distribution,
                    problem_population=city_details["population"],
                    problem_age_distribution=age_distribution,
                    problem_start_number_of_active_cases=case.problem_start_number_of_active_cases,
                    problem_end_number_of_active_cases=case.problem_end_number_of_active_cases,
                    problem_start_number_of_icu_active_cases=case.problem_start_number_of_icu_active_cases,
                    problem_end_number_of_icu_active_cases=case.problem_end_number_of_icu_active_cases,
                    problem_start_number_of_deaths=case.problem_start_number_of_deaths,
                    problem_end_number_of_deaths=case.problem_end_number_of_deaths,
                    problem_vaccinated_population=case.problem_vaccinated_population,
                    problem_infection_rate=infection_rate,
                    problem_mortality_rate=mortality_rate,
                    problem_average_temprature=case.problem_average_temprature,
                    problem_average_humidity=case.problem_average_humidity,
                    solution_description=solution_description_template,
                    solution_lockdown_policy_level=case.solution_lockdown_policy_level,
                    solution_mask_policy_level=case.solution_mask_policy_level,
                    solution_vaccine_policy_level=case.solution_vaccine_policy_level,
                    solution_effectiveness=effectivness)

    session.add(caseAdd)
    session.commit()
    cases_query = session.query(Cases)
    cases_query.all()
    return {"result": caseAdd}





# @app.put("/cases/update/{id}")
# async def update_todo(
#     id: int,
#     new_text: str = "",
#     is_complete: bool = False
# ):
#     todo_query = session.query(Todo).filter(Todo.id==id)
#     todo = todo_query.first()
#     if new_text:
#         todo.text = new_text
#     todo.is_done = is_complete
#     session.add(todo)
#     session.commit()


@app.delete("/cases/delete/{id}")
async def delete_case(id: int):
    case = session.query(Cases).filter(Cases.id == id).first()
    session.delete(case)
    session.commit()
    return {"case deleted": case.id}

@app.get("/recommendation")
async def get_all_recommendation():
    recommendation_query = session.query(Recommendation)
    return ({"result": recommendation_query.all()})

@app.post("/recommendation")
def recommendation(case: CaseRecommendation):
    city_details = cityDetails.cities[case.city]
    a = case.__dict__
    a['problem_population'] = city_details['population']
    all_similar_date = similarity.find_similar_cases_by_distance(
        a, get_cases(), 4, 'euclidean')
    similar_data = all_similar_date[0]

    infection_rate = round((case.problem_start_number_of_active_cases /
                            city_details["population"]) * 100, 2)
    mortality_rate = round((case.problem_start_number_of_deaths /
                            city_details["population"]) * 100, 2)
    age_distribution, age_category = categorize.categorize_age(city_details["median_age"])
    density_distribution, density_category = categorize.categorize_density(
        city_details["median_age"], city_details["population"])
    effectivness = categorize.claculate_effectivness(case.problem_start_number_of_active_cases,
                                          case.problem_end_number_of_active_cases, case.problem_start_number_of_icu_active_cases, case.problem_end_number_of_icu_active_cases)

    p_description = f'Currently, the population density in this area is **{density_category}**. The total population in the affected area is **{city_details["population"]}**, and it has a **{age_category}** age distribution. There are currently **{case.problem_start_number_of_active_cases}** active cases of the disease in the area, out of which **{case.problem_start_number_of_icu_active_cases}** are severe cases. **{case.problem_start_number_of_deaths}** deaths have also been reported so far. The infection rate in this area is **{infection_rate} percentage** and the mortality rate is **{mortality_rate} percentage**.'

    lockdown_policy_description = categorize.lockdown_policy(
        similar_data['solution_lockdown_policy_level'])
    mask_policy_description = categorize.mask_policy(
        similar_data['solution_mask_policy_level'])
    vaccine_policy_description = categorize.vaccine_policy(
        similar_data['solution_vaccine_policy_level'])

    solution_description_template = f'In a scenario where the population density is **{density_category}**, age distribution is **{age_category}**, infection rate is **{infection_rate}** percentage, and mortality rate is **{mortality_rate} percentage**, **with {case.problem_start_number_of_icu_active_cases}** icu active cases. </br></br> It is recommended to implement a **level {similar_data["solution_lockdown_policy_level"]} lockdown policy**, {lockdown_policy_description}.</br> A **level {similar_data["solution_mask_policy_level"]} mask policy** {mask_policy_description}.</br> It is important to note that {vaccine_policy_description}. </br> Overall, taking these measures can help control the spread of the disease and minimize the number of severe cases and deaths in the affected area.'

    caseAdd = Recommendation(start_date=case.start_date,
                    end_date=case.end_date,
                    city=case.city,
                    problem_description=p_description,
                    problem_population_density=density_distribution,
                    problem_population=city_details["population"],
                    problem_age_distribution=age_distribution,
                    problem_start_number_of_active_cases=case.problem_start_number_of_active_cases,
                    problem_end_number_of_active_cases=case.problem_end_number_of_active_cases,
                    problem_start_number_of_icu_active_cases=case.problem_start_number_of_icu_active_cases,
                    problem_end_number_of_icu_active_cases=case.problem_end_number_of_icu_active_cases,
                    problem_start_number_of_deaths=case.problem_start_number_of_deaths,
                    problem_end_number_of_deaths=case.problem_end_number_of_deaths,
                    problem_vaccinated_population=case.problem_vaccinated_population,
                    problem_infection_rate=infection_rate,
                    problem_mortality_rate=mortality_rate,
                    problem_average_temprature=case.problem_average_temprature,
                    problem_average_humidity=case.problem_average_humidity,
                    solution_description=solution_description_template,
                    solution_lockdown_policy_level=similar_data['solution_lockdown_policy_level'],
                    solution_mask_policy_level=similar_data['solution_mask_policy_level'],
                    solution_vaccine_policy_level=similar_data['solution_vaccine_policy_level'],
                    solution_effectiveness=effectivness)

    session.add(caseAdd)
    session.commit()
    cases_query = session.query(Recommendation)
    return ({"recommendation": solution_description_template,
             "most_similar":[{
                "top_1" : all_similar_date[1]['solution_description'],
                "top_2" : all_similar_date[2]['solution_description'],
                "top_3" : all_similar_date[3]['solution_description'],
             }]})

@app.delete("/recommendation/{id}")
async def delete_recommendation(id: int):
    case = session.query(Recommendation).filter(Recommendation.id == id).first()
    session.delete(case)
    session.commit()
    return {"Recommendation deleted": case.id}

@app.get("/cityDetails/{name}")
async def get_city_details(name: str):
    city = cityDetails.cities[name]
    return city
