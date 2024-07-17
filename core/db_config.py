from pydantic_settings import BaseSettings

from .env import get_environment_variables

env = get_environment_variables()


class DBSettings(BaseSettings):
    """Config of DB."""

    DB_URL: str = f"sqlite+aiosqlite:///{env.DATABASE_NAME}"
    DB_ECHO: bool = False


db_settings = DBSettings()
