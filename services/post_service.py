from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Optional, Callable

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import dto, orm


class PostService:

    __slots__: tuple[str] = ("_orm_session", )

    def __init__(self, orm_session: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        self._orm_session = orm_session

    async def get_post(self, id: int) -> Optional[dto.GetPostResponse]:
        async with self._orm_session() as session:
            result: Optional[orm.Post] = await session.get(orm.Post, id)
            if result is None:
                return None
            return dto.GetPostResponse(
                id=result.id,
                title=result.title,
                created_date=result.created_date,
                updated_date=result.updated_date,
                count_of_comments=len(result.comments)
            )

    async def create_post(self, data: dto.CreatePostRequest) -> None:
        async with self._orm_session() as session:
            async with session.begin():
                session.add(orm.Post(
                    title=data.title,
                    article=data.article
                ))

    async def update_post(self, data: dto.UpdatePostRequest) -> bool:
        async with self._orm_session() as session:
            async with session.begin():
                result = await session.execute(
                    sa.update(orm.Post)
                    .where(orm.Post.id == data.id)
                    .values(title=data.new_title, article=data.new_article, updated_date=datetime.utcnow())
                    .execution_options(synchronize_session="fetch")
                )
                return bool(result.rowcount)

    async def delete_post(self, id: int) -> bool:
        async with self._orm_session() as session:
            async with session.begin():
                result = await session.execute(
                    sa.delete(orm.Post)
                    .where(orm.Post.id == id)
                )
                return bool(result.rowcount)
