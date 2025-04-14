from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from constants import EnvFileLocation


class DBConfig(BaseModel):
    db_url: str
    echo: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_nested_delimiter="__",
        env_file=(EnvFileLocation.LOCATION),
    )

    DB_CONFIG: DBConfig


settings = Settings()
