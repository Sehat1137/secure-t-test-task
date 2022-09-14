import asyncio
import os
from contextlib import AbstractAsyncContextManager
from typing import Callable

import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

import views.comment
import views.post
from config import Config
from tools.container import Container
from tools.exceptions_handlers import exception_handler


@pytest.fixture(autouse=True)
def event_loop():
    ev_loop = asyncio.get_event_loop()
    yield ev_loop
    ev_loop.close()


@pytest.fixture
def config() -> Config:
    os.environ["POSTGRES_DB"] = "testdb"
    os.environ["POSTGRES_HOST"] = "test_db"
    os.environ["POSTGRES_PORT"] = "5432"
    os.environ["POSTGRES_USER"] = "testdb"
    os.environ["POSTGRES_PASSWORD"] = "testdb"
    return Config()


@pytest.fixture(autouse=True)
def container(config: Config) -> Container:
    container = Container()
    container.config.from_pydantic(Config())
    container.wire(modules=["views.post", "views.comment"])
    container.init_resources()
    with container.connection_string.override("sqlite+aiosqlite://"):
        yield container
    container.unwire()


@pytest.fixture
def session_factory(container: Container) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
    return container.orm.provided.session()


@pytest.fixture(autouse=True)
async def db(container: Container):
    db = container.orm()
    await db.create_database()
    yield
    await db._drop_database()


@pytest.fixture
def app(container: Container) -> FastAPI:
    application = FastAPI(
        exception_handlers={Exception: exception_handler}
    )
    router = APIRouter(
        prefix="/api/v1",
        responses={
            500: {"description": "Server error"},
            404: {"description": "Something not found"},
        },
    )
    router.include_router(
        views.post.get_router()
    )
    router.include_router(
        views.comment.get_router()
    )
    application.include_router(router)
    return application


@pytest.fixture
async def client(app: FastAPI) -> TestClient:
    async with TestClient(app) as client:
        yield client
