from typing import Optional

from pydantic import PostgresDsn, BaseModel


class DatabaseSettings(BaseModel):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: str
    DB_NAME: str

    ECHO_LOG: bool = False

    @property
    def async_connect_url(self) -> Optional[PostgresDsn]:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB_NAME}"
