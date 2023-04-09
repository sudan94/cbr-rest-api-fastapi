from fastapi import FastAPI
from models import Cases, session
from pydantic import BaseModel
import cityDetails
from fastapi.middleware.cors import CORSMiddleware


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
    solution_lockdown_policy_level: int
    solution_mask_policy_level: int
    solution_vaccine_policy_level: int


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


@app.post("/cases/create")
async def create_case(case:Case):

    city_details = cityDetails.cities[case.city]
    infection_rate = (case.problem_start_number_of_active_cases /
                      city_details["population"]) * 100
    mortality_rate = (case.problem_start_number_of_active_cases /
                      city_details["population"]) * 100
    age_distribution = categorize_age(city_details["median_age"])
    density_distribution = categorize_density(
        city_details["median_age"], city_details["population"])
    effectivness = claculate_effectivness(case.problem_start_number_of_active_cases,
                                         case.problem_end_number_of_active_cases, case.problem_start_number_of_deaths, case.problem_end_number_of_deaths)

    p_description = f'Currently, the population density in this area is {density_distribution}. The total population in the affected area is {city_details["population"]}, and it has a {age_distribution}. There are currently {case.problem_start_number_of_active_cases} active cases of the disease in the area, out of which {case.problem_start_number_of_icu_active_cases} are severe cases. Unfortunately, {case.problem_start_number_of_deaths} deaths have also been reported so far. The population in the affected area has not yet received any vaccination, as {case.problem_vaccinated_population}. The infection rate in this area is {infection_rate}, which is a positive sign. However, the mortality rate is {mortality_rate}, which is concerning. Therefore, it is crucial to take necessary precautions and measures to prevent the further spread of the disease and minimize the mortality rate.'

    # Define the lockdown policy description based on the lockdown policy level
    if case.solution_lockdown_policy_level == 0:
        lockdown_policy_description = "No measures"
    elif case.solution_lockdown_policy_level == 1:
        lockdown_policy_description = "Recommend not leaving house"
    elif case.solution_lockdown_policy_level == 2:
        lockdown_policy_description = "Require not leaving house with exceptions for daily exercise, grocery shopping, and ‘essential’ trips"
    else:
        lockdown_policy_description = "Require not leaving house with minimal exceptions (e.g., allowed to leave only once every few days, or only one person can leave at a time, etc.)not implementing any lockdown policy."

    # Define the mask policy description based on the mask policy level
    if case.solution_mask_policy_level == 0:
        mask_policy_description = "No measure"
    elif case.solution_mask_policy_level == 1:
        mask_policy_description = "Recommended"
    elif case.solution_mask_policy_level == 2:
        mask_policy_description = " Required in some specified shared/public spaces outside the home with other people present, or some situations when social distancing not possible."
    elif case.solution_mask_policy_level == 3:
        mask_policy_description = "Required in all shared/public spaces outside the home with other people present or all situations when social distancing not possible"
    else:
        mask_policy_description = "Required outside the home at all times, regardless of location or presence of other people."

    # Define the vaccine policy description based on the mask policy level
    if case.solution_vaccine_policy_level == 0:
        vaccine_policy_description = "No availability"
    elif case.solution_vaccine_policy_level == 1:
        vaccine_policy_description = "Availability for ONE of the following: key workers/ clinically vulnerable groups / elderly groups"
    elif case.solution_vaccine_policy_level == 2:
        vaccine_policy_description = "Availability for TWO of the following: key workers/ clinically vulnerable groups / elderly groups"
    elif case.solution_vaccine_policy_level == 3:
        vaccine_policy_description = " Availability for ALL the following: key workers/ clinically vulnerable groups / elderly groups"
    else:
        vaccine_policy_description = "Availability for all three, plus partial additional availability (select broad groups/ages)"

    solution_description_template = f'In a scenario where the population density is {density_distribution}, age distribution is {age_distribution}, infection rate is {infection_rate}, and mortality rate is {mortality_rate}, with {case.problem_start_number_of_active_cases} severe active cases, it is recommended to take necessary precautions to prevent the further spread of the disease. Furthermore, it is recommended to implement a Level {case.solution_lockdown_policy_level} lockdown policy, which involves {lockdown_policy_description}. A Level {case.solution_mask_policy_level} mask policy should also be implemented, requiring individuals to {mask_policy_description}. It is important to note that {vaccine_policy_description}.Overall, taking these measures can help control the spread of the disease and minimize the number of severe cases and deaths in the affected area.'

    caseAdd = Cases(start_date=case.start_date,
                 end_date=case.end_date,
                 city=case.city,
                 problem_description=p_description,
                 problem_population_density=density_distribution,
                 problem_population=city_details["population"],
                 problem_age_distribution=age_distribution,
                 problem_start_number_of_active_cases=case.problem_start_number_of_active_cases,
                 problem_end_number_of_active_cases=case.problem_end_number_of_active_cases,
                 problem_start_number_of_icu_active_cases=case.problem_start_number_of_icu_active_cases, problem_end_number_of_icu_active_cases=case.problem_end_number_of_icu_active_cases,
                 problem_start_number_of_deaths=case.problem_start_number_of_deaths,
                 problem_end_number_of_deaths=case.problem_end_number_of_deaths,
                 problem_vaccinated_population=case.problem_vaccinated_population,
                 problem_infection_rate=infection_rate,
                 problem_mortality_rate=mortality_rate,
                 problem_weather="TBD",
                 solution_description=solution_description_template,
                 solution_lockdown_policy_level=case.solution_lockdown_policy_level,
                 solution_mask_policy_level=case.solution_mask_policy_level,
                 solution_vaccine_policy_level=case.solution_vaccine_policy_level,
                 solution_effectiveness=effectivness)

    session.add(caseAdd)
    session.commit()
    cases_query = session.query(Cases)
    cases_query.all()
    return {"status": "success"}


@app.get("/cases")
async def get_all_cases():
    cases_query = session.query(Cases)
    return ({"data": cases_query.all()})


@app.get("/cityDetails/{name}")
async def get_city_details(name: str):
    a = cityDetails.cities[name]
    return a["population"]


def categorize_age(medain_age):
    if (medain_age > 30):
        return 3
    elif (medain_age >= 20 and medain_age <= 30):
        return 2
    elif (medain_age >= 1 and medain_age < 20):
        return 1
    else:
        return 0


def categorize_density(density, population):
    if (population >= 50000 and density >= 1500):
        return 3
    elif (population >= 5000 and density >= 300):
        return 2
    elif (density < 300):
        return 1
    else:
        return 0


def claculate_effectivness(start_case, end_case, start_death, end_death):
    diff_death = start_death - end_death
    if end_case < start_case:
        return 3
    elif end_case == start_case:
        return 2
    elif end_case > start_case:
        return 1
    else:
        return 0


# def categorize_date(data):
#     if(data['density'] > 1500)


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
