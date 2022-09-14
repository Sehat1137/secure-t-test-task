from typing import Optional

from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse

import views.comment
import views.post
from config import Config
from tools.container import Container
from tools.exceptions_handlers import exception_handler


class App:

    __slots__ = ("_container", "_api")

    def __init__(self) -> None:
        self._container: Container = Container()
        self._api: Optional[FastAPI] = None

    def _init_container(self) -> None:
        self._container.config.from_pydantic(Config())
        self._container.wire(modules=["views.post", "views.comment"])
        self._container.init_resources()

    async def _init_db(self):
        orm = self._container.orm()
        await orm.create_database()

    def _init_api(self) -> None:
        self._api = FastAPI(
            default_response_class=ORJSONResponse,
            exception_handlers={Exception: exception_handler}
        )
        router = APIRouter(
            prefix="/api/v1",
            responses={
                500: {"description": "Server error"},
                404: {"description": "Something not found"},
            },
            on_startup=[
                self._init_db
            ]
        )
        router.include_router(
            views.post.get_router()
        )
        router.include_router(
            views.comment.get_router()
        )
        self._api.include_router(router)

    @classmethod
    def get_app(cls):
        app: "App" = cls()
        app._init_container()
        app._init_api()
        return app._api
