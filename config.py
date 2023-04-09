# config.py
from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER : str # default value if env variable does not exist
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str # default value if env variable does not exist
    POSTGRES_DRIVERNMAE : str
    POSTGRES_HOSTNAME : str
    DATABASE_PORT : int

# specify .env file location as Config attribute
    class Config:
        env_file = ".env"