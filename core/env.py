from functools import lru_cache

from pydantic_settings import BaseSettings


class EnvSettings(BaseSettings):
    """Environment variables."""

    # Database.
    DATABASE_NAME: str

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


@lru_cache
def get_environment_variables() -> EnvSettings:
    return EnvSettings()
