from fastapi import APIRouter
from pydantic import BaseModel
import cityDetails
import categorize
from models import Cases, session
import pandas as pd

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

router = APIRouter()

def get_cases():
    all_cases = []
    cases_query = session.query(Cases)
    for i in cases_query.all():
        all_cases.append(i.__dict__)
    return all_cases

@router.get("/cases")
async def get_all_cases():
    cases_query = session.query(Cases)
    return ({"data": cases_query.all()})

@router.post("/cases/create")
async def create_case(case: Case):

    city_details = cityDetails.cities[case.city]
    infection_rate = round((case.problem_start_number_of_active_cases /
                            city_details["population"]) * 100, 2)
    mortality_rate = round((case.problem_start_number_of_deaths /
                            city_details["population"]) * 100, 2)
    # age_distribution, age_category = categorize.categorize_age(city_details["median_age"])
    density_distribution, density_category = categorize.categorize_density(
        city_details["density"], city_details["population"])
    effectivness = categorize.claculate_effectivness(case.problem_start_number_of_active_cases, case.problem_end_number_of_active_cases,
                                          case.problem_start_number_of_icu_active_cases, case.problem_end_number_of_icu_active_cases)

    lockdown_policy_description = categorize.lockdown_policy(
        case.solution_lockdown_policy_level)
    mask_policy_description = categorize.mask_policy(case.solution_mask_policy_level)
    vaccine_policy_description = categorize.vaccine_policy(
        case.solution_vaccine_policy_level)

    p_description = f'Currently, the population density in this area is **{density_category}**. The total population in the affected area is **{city_details["population"]}**, and it has a **{city_details["median_age"]}** median age distribution. There are currently **{case.problem_start_number_of_active_cases}** active cases of the disease in the area, out of which **{case.problem_start_number_of_icu_active_cases}** are severe cases. **{case.problem_start_number_of_deaths}** deaths have also been reported so far. The infection rate in this area is **{infection_rate} percentage** and the mortality rate is **{mortality_rate} percentage**.'

    solution_description_template = f'In a scenario where the population density is **{density_category}**, median age is **{city_details["median_age"]}**, infection rate is **{infection_rate}** percentage, and mortality rate is **{mortality_rate} percentage**, **with {case.problem_start_number_of_icu_active_cases}** icu active cases.  \nIt is recommended to implement a **level {case.solution_lockdown_policy_level} lockdown policy**, {lockdown_policy_description}.  \nA **level {case.solution_mask_policy_level} mask policy** {mask_policy_description}.  \nIt is important to note that {vaccine_policy_description}.  \nOverall, taking these measures can help control the spread of the disease and minimize the number of severe cases and deaths in the affected area.'

    caseAdd = Cases(start_date=case.start_date,
                    end_date=case.end_date,
                    city=case.city,
                    problem_description=p_description,
                    problem_population_density=density_distribution,
                    problem_population=city_details["population"],
                    problem_age_distribution=city_details["median_age"],
                    problem_start_number_of_active_cases=case.problem_start_number_of_active_cases,
                    problem_end_number_of_active_cases=case.problem_end_number_of_active_cases,
                    problem_start_number_of_icu_active_cases=case.problem_start_number_of_icu_active_cases,
                    problem_end_number_of_icu_active_cases=case.problem_end_number_of_icu_active_cases,
                    problem_start_number_of_deaths=case.problem_start_number_of_deaths,
                    problem_end_number_of_deaths=case.problem_end_number_of_deaths,
                    problem_vaccinated_population=case.problem_vaccinated_population,
                    problem_infection_rate=infection_rate,
                    problem_mortality_rate=mortality_rate,
                    problem_average_temperature=case.problem_average_temperature,
                    problem_average_humidity=case.problem_average_humidity,
                    solution_description=solution_description_template,
                    solution_lockdown_policy_level=case.solution_lockdown_policy_level,
                    solution_mask_policy_level=case.solution_mask_policy_level,
                    solution_vaccine_policy_level=case.solution_vaccine_policy_level,
                    solution_effectiveness=effectivness)

    session.add(caseAdd)
    try:
        session.commit()
    except:
        session.rollback()
        raise
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


@router.delete("/cases/delete/{id}")
async def delete_case(id: int):
    case = session.query(Cases).filter(Cases.id == id).first()
    session.delete(case)
    session.commit()
    return {"case deleted": case.id}

@router.get("/bulkCases")
def create_bulk_cases_csv():
    df = pd.read_csv("data/data.csv",index_col=0)
    for index, row in df.iterrows():
        city_details = cityDetails.cities[row["city"]]
        infection_rate = round((row["problem_start_number_of_active_cases"] /
                            city_details["population"]) * 100, 2)
        mortality_rate = round((row["problem_start_number_of_deaths"] /
                            city_details["population"]) * 100, 2)
        # age_distribution, age_category = categorize.categorize_age(city_details["median_age"])
        density_distribution, density_category = categorize.categorize_density(
        city_details["density"], city_details["population"])
        effectivness = categorize.claculate_effectivness(row["problem_start_number_of_active_cases"], row["problem_end_number_of_active_cases"],
                                         row["problem_start_number_of_icu_active_cases"],row["problem_end_number_of_icu_active_cases"])

        lockdown_policy_description = categorize.lockdown_policy(
        row["problem_start_number_of_icu_active_cases"])
        mask_policy_description = categorize.mask_policy(row["solution_mask_policy_level"])
        vaccine_policy_description = categorize.vaccine_policy(
        row["solution_vaccine_policy_level"])

        p_description = f'Currently, the population density in this area is **{density_category}**. The total population in the affected area is **{city_details["population"]}**, and it has a **{city_details["median_age"]}** median age distribution. There are currently **{row["problem_start_number_of_active_cases"]}** active cases of the disease in the area, out of which **{row["problem_start_number_of_icu_active_cases"]}** are severe cases. **{row["problem_start_number_of_deaths"]}** deaths have also been reported so far. The infection rate in this area is **{infection_rate} percentage** and the mortality rate is **{mortality_rate} percentage**.'

        solution_description_template = f'In a scenario where the population density is **{density_category}**, median age is **{city_details["median_age"]}**, infection rate is **{infection_rate}** percentage, and mortality rate is **{mortality_rate} percentage**, **with {int(row["problem_start_number_of_icu_active_cases"])}** icu active cases.  \nIt is recommended to implement a **level {int(row["solution_lockdown_policy_level"])} lockdown policy**, {lockdown_policy_description}.  \nA **level {int(row["solution_mask_policy_level"])} mask policy** {mask_policy_description}.  \nIt is important to note that {vaccine_policy_description}.  \nOverall, taking these measures can help control the spread of the disease and minimize the number of severe cases and deaths in the affected area.'
        caseAdd = Cases(start_date=row["start_date"],
                    end_date=row["end_date"],
                    city=row["city"],
                    problem_description=p_description,
                    problem_population_density=density_distribution,
                    problem_population=city_details["population"],
                    problem_age_distribution=city_details["median_age"],
                    problem_start_number_of_active_cases=row["problem_start_number_of_active_cases"],
                    problem_end_number_of_active_cases=row["problem_end_number_of_active_cases"],
                    problem_start_number_of_icu_active_cases=row["problem_start_number_of_icu_active_cases"],
                    problem_end_number_of_icu_active_cases=row["problem_end_number_of_icu_active_cases"],
                    problem_start_number_of_deaths=row["problem_start_number_of_deaths"],
                    problem_end_number_of_deaths=row["problem_end_number_of_deaths"],
                    problem_vaccinated_population=row["problem_vaccinated_population"],
                    problem_infection_rate=infection_rate,
                    problem_mortality_rate=mortality_rate,
                    problem_average_temperature=round(row["problem_average_temperature"],2),
                    problem_average_humidity=round(row["problem_average_humidity"],2),
                    solution_description=solution_description_template,
                    solution_lockdown_policy_level=row["solution_lockdown_policy_level"],
                    solution_mask_policy_level=row["solution_mask_policy_level"],
                    solution_vaccine_policy_level=row["solution_vaccine_policy_level"],
                    solution_effectiveness=effectivness)

        session.add(caseAdd)
        try:
            session.commit()
        except:
            session.rollback()
            raise
    return {"message": "ok"}