from fastapi import FastAPI
from models import Cases, session
import json

app = FastAPI()

@app.post("/cases/create")
async def create_case(start_date: str, end_date: str, city:str, problem_description : str, problem_population_density : int, problem_population : int, problem_age_distribution: int, problem_number_of_active_cases: int, problem_number_of_severe_active_cases: int, problem_number_of_deaths: int, problem_vaccinated_population: int, problem_weather: str, solution_description: str, solution_lockdown_policy_level: int, solution_mask_policy_level:int, solution_vaccine_policy_level: int, solution_effectiveness:int):
    infection_rate = (problem_number_of_active_cases / problem_population) * 100
    mortality_rate = (problem_number_of_deaths / problem_population) * 100
    case = Cases(start_date = start_date, end_date = end_date, city = city,problem_description = problem_description, problem_population_density = problem_population_density,problem_population = problem_population,problem_age_distribution = problem_age_distribution, problem_number_of_active_cases = problem_number_of_active_cases,problem_number_of_severe_active_cases = problem_number_of_severe_active_cases,problem_number_of_deaths = problem_number_of_deaths,problem_vaccinated_population = problem_vaccinated_population,problem_infection_rate = infection_rate ,problem_mortality_rate = mortality_rate,problem_weather = problem_weather,solution_description = solution_description,solution_lockdown_policy_level = solution_lockdown_policy_level,solution_mask_policy_level = solution_mask_policy_level,solution_vaccine_policy_level = solution_vaccine_policy_level,solution_effectiveness = solution_effectiveness)
    session.add(case)
    session.commit()
    cases_query = session.query(Cases)
    cases_query.all()
    return {"status": "success"}

@app.get("/cases")
async def get_all_cases():
    cases_query = session.query(Cases)
    return ({"data":cases_query.all()})

@app.get("/cityDetails/{name}")
async def get_city_details(name : str):
    # Opening JSON file
    f = open('cityDetails.json')
    data = json.load(f)
    citydetails = data[name]
    # Closing file
    f.close()
    return ({'data':citydetails})


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
    case = session.query(Cases).filter(Cases.id==id).first()
    session.delete(case)
    session.commit()
    return {"case deleted": case.id}