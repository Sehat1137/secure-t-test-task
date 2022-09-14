import asyncio
import logging
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import orm
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ORM:

    @staticmethod
    def get_connection_string(host: str, port: int, user: str, password: str, db_name: str):
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

    def __init__(self, connection_string: str) -> None:
        self._engine: AsyncEngine = create_async_engine(connection_string, future=True)
        self._session_factory = async_scoped_session(
            orm.sessionmaker(
                self._engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
            ),
            scopefunc=asyncio.current_task
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _drop_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            logging.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()
