from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Optional, Callable

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import orm, dto


class CommentService:

    __slots__: tuple[str] = ("_orm_session", )

    def __init__(self, orm_session: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        self._orm_session = orm_session

    async def get_comments(self, post_id: int, nesting_level: int) -> Optional[list[dto.GetCommentsResponse]]:
        async with self._orm_session() as session:
            post: Optional[orm.Post] = await session.get(orm.Post, post_id)
        if post is None:
            return None

        result = []
        for c in post.comments:
            if c.nesting_level == nesting_level:
                result.append(
                    dto.comment.GetCommentsResponse(
                        id=c.id,
                        author=c.author,
                        body=c.body,
                        is_deleted=c.is_deleted,
                        nesting_level=c.nesting_level,
                        parent_comment_id=c.parent_comment_id,
                        created_date=c.created_date,
                        updated_date=c.updated_date,
                        post_id=c.post_id
                    )
                )
        return result

    async def create_comment(self, data: dto.CreateCommentRequest) -> dto.CreateCommentStatus:
        async with self._orm_session() as session:
            post: Optional[orm.Post] = await session.get(orm.Post, data.post_id)

        if post is None:
            return dto.CreateCommentStatus(status=False, reason="Reply to unknown post")
        nesting_level = 0
        if data.parent_comment_id > 0:
            comment: Optional[orm.Comment] = None
            for c in post.comments:
                if c.id == data.parent_comment_id:
                    nesting_level = c.nesting_level + 1
                    comment = c
                    break
            if comment is None or comment.is_deleted:
                return dto.CreateCommentStatus(status=False, reason="Reply to unknown comment")

        async with self._orm_session() as session:
            async with session.begin():
                session.add(orm.Comment(
                    author=data.author,
                    body=data.body,
                    nesting_level=nesting_level,
                    parent_comment_id=data.parent_comment_id,
                    post_id=data.post_id
                ))
            return dto.CreateCommentStatus(status=True)

    async def update_comment(self, data: dto.UpdateCommentRequest) -> bool:
        async with self._orm_session() as session:
            async with session.begin():
                result = await session.execute(
                    sa.update(orm.Comment)
                    .where(orm.Comment.id == data.id)
                    .values(body=data.new_body, updated_date=datetime.utcnow())
                    .execution_options(synchronize_session="fetch")
                )
                return bool(result.rowcount)

    async def delete_comment(self, id: int) -> bool:
        async with self._orm_session() as session:
            async with session.begin():
                result = await session.execute(
                    sa.update(orm.Comment)
                    .where(
                        (orm.Comment.id == id) &
                        (orm.Comment.is_deleted == False)
                    )
                    .values(author="Unknown", body="Comment was deleted", is_deleted=True)
                    .execution_options(synchronize_session="fetch")
                )
                return bool(result.rowcount)

    async def get_children(self, parent_comment_id: int) -> list[dto.GetCommentsResponse]:
        async with self._orm_session() as session:
            comments = await session.execute(
                sa.select(orm.Comment).where(orm.Comment.parent_comment_id == parent_comment_id)
            )
        result = []
        for row in comments:
            for comment in row:
                result.append(
                    dto.comment.GetCommentsResponse(
                        id=comment.id,
                        author=comment.author,
                        body=comment.body,
                        is_deleted=comment.is_deleted,
                        nesting_level=comment.nesting_level,
                        parent_comment_id=comment.parent_comment_id,
                        created_date=comment.created_date,
                        updated_date=comment.updated_date,
                        post_id=comment.post_id
                    )
                )
        return result
