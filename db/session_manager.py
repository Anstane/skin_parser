import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import db_settings


class DBSessionManager:
    """Manager of DB sessions."""

    def __init__(self, url: str, echo: bool):
        self._engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autocommit=False,
        )

    async def close(self):
        if self._engine is None:
            raise Exception("Engine is None.")
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    @contextlib.asynccontextmanager
    async def connection(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("Engine is None.")
        async with self._engine.connect() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise Exception("Exception in connection.")

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_factory is None:
            raise Exception("Session factory is None.")
        async with self._session_factory() as session:
            try:
                yield session
            except Exception as er:
                await session.rollback()
                raise er
            finally:
                await session.close()


db_session_manager = DBSessionManager(url=db_settings.DB_URL, echo=db_settings.DB_ECHO)


async def db_get_session():
    async with db_session_manager.session() as session:
        yield session
