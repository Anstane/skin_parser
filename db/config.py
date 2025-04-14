from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings


class DatabaseConfig:
    def __init__(
        self,
        connect_url: str,
        echo: bool = False,
    ):
        self.engine = create_async_engine(
            url=connect_url,
            echo=echo,
            poolclass=NullPool,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False,
        )

    async def get_async_session(self):
        async with self.session_factory() as session:
            yield session


db_helper = DatabaseConfig(
    connect_url=str(settings.DB_CONFIG.db_url),
    echo=settings.DB_CONFIG.echo,
)
