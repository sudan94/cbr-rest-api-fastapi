from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, SmallInteger, Float, Text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from functools import lru_cache
import config

@lru_cache()
def get_settings():
    return config.Settings()

env = get_settings()

url = URL.create(
    drivername=env.POSTGRES_DRIVERNMAE,
    username=env.POSTGRES_USER,
    password=env.POSTGRES_PASSWORD,
    host=env.POSTGRES_HOSTNAME,
    database=env.POSTGRES_DB,
    port=5432
)

engine = create_engine(url)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Cases(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    start_date = Column(Date)
    end_date = Column(Date)
    city = Column(String)
    problem_description = Column(Text)
    problem_population_density = Column(Integer)
    problem_population = Column(Integer)
    problem_age_distribution = Column(SmallInteger)
    problem_start_number_of_active_cases = Column(Integer)
    problem_end_number_of_active_cases = Column(Integer)
    problem_start_number_of_icu_active_cases = Column(Integer)
    problem_end_number_of_icu_active_cases = Column(Integer)
    problem_start_number_of_deaths= Column(Integer)
    problem_end_number_of_deaths = Column(Integer)
    problem_vaccinated_population = Column(Integer)
    problem_infection_rate = Column(Float)
    problem_mortality_rate = Column(Float)
    problem_average_temprature = Column(String)
    problem_average_humidity = Column(String)
    solution_description = Column(Text)
    solution_lockdown_policy_level = Column(Integer)
    solution_mask_policy_level = Column(Integer)
    solution_vaccine_policy_level = Column(Integer)
    solution_effectiveness = Column(Integer)

Base.metadata.create_all(engine)