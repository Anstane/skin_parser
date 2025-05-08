from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.constants import EnvFileLocation
from app.config.postgres import DatabaseSettings


class Telegram(BaseModel):
    TOKEN: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_nested_delimiter="__",
        env_file=(EnvFileLocation.LOCATION),
    )

    POSTGRES: DatabaseSettings
    TELEGRAM: Telegram


settings = Settings()
