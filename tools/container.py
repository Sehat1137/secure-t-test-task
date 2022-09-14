from typing import Union

from dependency_injector import containers, providers

from config import Config
from services import CommentService, PostService
from tools.orm import ORM


class Container(containers.DeclarativeContainer):

    config: Union[providers.Configuration[Config], Config] = providers.Configuration()

    connection_string: providers.Resource[str] = providers.Resource(
        ORM.get_connection_string,
        host=config.postgres.host,
        port=config.postgres.port,
        user=config.postgres.user,
        password=config.postgres.password,
        db_name=config.postgres.db
    )

    orm: providers.Singleton[ORM] = providers.Singleton(
        ORM,
        connection_string=connection_string
    )

    post_service: providers.Resource[PostService] = providers.Factory(
        PostService,
        orm_session=orm.provided.session
    )

    comment_service: providers.Resource[CommentService] = providers.Factory(
        CommentService,
        orm_session=orm.provided.session
    )
