from contextlib import AbstractAsyncContextManager
from typing import Callable

import pytest
import sqlalchemy as sa
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import orm

pytestmark = pytest.mark.asyncio


async def test_comment_fetch(
        client: TestClient,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
) -> None:

    def fixtures():
        session.add_all([
            orm.Post(id=1, title="title", article="big article"),
            orm.Comment(
                id=1, author="author 1", body="awesome comment", post_id=1, nesting_level=0, parent_comment_id=0
            ),
            orm.Comment(
                id=2,
                author="Unknown",
                body="Comment was deleted",
                post_id=1,
                nesting_level=1,
                parent_comment_id=1,
                is_deleted=True
            ),
            orm.Comment(id=3, author="author 4", body="just comment", post_id=1, nesting_level=2, parent_comment_id=2),
            orm.Comment(id=4, author="author 5", body=")", post_id=1, nesting_level=3, parent_comment_id=3),
        ])

    async with session_factory() as session:
        async with session.begin():
            fixtures()

    for x in range(4):
        result = await client.get("/api/v1/comment/fetch", query_string={"post_id": 1, "nesting_level": x})
        data = result.json()
        assert result.status_code == 200 and len(data) == 1
        comment = data[0]
        assert comment["id"] == x + 1
        assert comment["parent_comment_id"] == x
        assert comment["nesting_level"] == x


async def test_comment_fetch_404(client: TestClient) -> None:
    result = await client.get("/api/v1/comment/fetch", query_string={"post_id": 1, "nesting_level": 0})
    assert result.status_code == 404


@pytest.mark.parametrize("comment", [
    {"parent_comment_id": 0, "nesting_level": 0},
    {"parent_comment_id": 1, "nesting_level": 1},
    {"parent_comment_id": 2, "nesting_level": 2},
])
async def test_comment_create(
        client: TestClient,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        comment: dict[str, int]
) -> None:

    def fixtures():
        session.add_all([
            orm.Post(id=1, title="title", article="big article"),
            orm.Comment(id=1, author="test1", body="test1", parent_comment_id=0, nesting_level=0, post_id=1),
            orm.Comment(id=2, author="test2", body="test2", parent_comment_id=1, nesting_level=1, post_id=1),
            orm.Comment(id=3, author="test3", body="test3", parent_comment_id=2, nesting_level=2, post_id=1)
        ])

    async with session_factory() as session:
        async with session.begin():
            fixtures()

        result = await client.post(
            "/api/v1/comment/create",
            json={"author": "test", "body": "test", "parent_comment_id": comment["parent_comment_id"], "post_id": 1}
        )
        assert result.status_code == 201
        comment = await session.execute(
            sa.select(orm.Comment)
            .where(
                (orm.Comment.nesting_level == comment["nesting_level"]) &
                (orm.Comment.parent_comment_id == comment["parent_comment_id"])
            )
        )
        assert comment is not None


@pytest.mark.parametrize("comment", [
    {"parent_comment_id": 10, "post_id": 1},
    {"parent_comment_id": 1, "post_id": 10},
])
async def test_comment_create_404(
        client: TestClient,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        comment: dict[str, int]
) -> None:

    def fixtures():
        session.add_all([
            orm.Post(id=1, title="title", article="big article"),
            orm.Comment(id=1, author="test1", body="test1", parent_comment_id=0, nesting_level=0, post_id=1)
        ])

    async with session_factory() as session:
        async with session.begin():
            fixtures()

    result = await client.post(
        "/api/v1/comment/create",
        json={
            "author": "test",
            "body": "test",
            "parent_comment_id": comment["parent_comment_id"],
            "post_id": comment["post_id"]
        }
    )
    assert result.status_code == 404


async def test_comment_update(
    client: TestClient,
    session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
) -> None:

    def fixtures():
        session.add_all([
            orm.Post(id=1, title="title", article="big article"),
            orm.Comment(id=1, author="title", body="body", parent_comment_id=0, nesting_level=0, post_id=1),
        ])

    async with session_factory() as session:
        async with session.begin():
            fixtures()

        result = await client.put("/api/v1/comment/update", json={"new_body": "new body", "id": 1})
        comment = await session.get(orm.Comment, 1)
        assert result.status_code == 204
        assert comment is not None
        assert comment.body == "new body"
        assert comment.updated_date is not None


async def test_comment_update_404(client: TestClient) -> None:
    result = await client.put("/api/v1/comment/update", json={"new_body": "new body", "id": 1})
    assert result.status_code == 404


async def test_comment_remove(
    client: TestClient,
    session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
) -> None:

    def fixtures():
        session.add_all([
            orm.Post(id=1, title="title", article="big article"),
            orm.Comment(id=1, author="title", body="body", parent_comment_id=0, nesting_level=0, post_id=1),
        ])

    async with session_factory() as session:
        async with session.begin():
            fixtures()

        result = await client.delete("/api/v1/comment/remove", query_string={"id": 1})
        comment = await session.get(orm.Comment, 1)
        assert result.status_code == 204
        assert comment.is_deleted
        assert comment.author == "Unknown"
        assert comment.body == "Comment was deleted"


async def test_comment_remove_404(client: TestClient) -> None:
    result = await client.delete("/api/v1/comment/remove", query_string={"id": 1})
    assert result.status_code == 404


async def test_comment_children(
    client: TestClient,
    session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
) -> None:

    def fixtures():
        session.add_all([
            orm.Post(id=1, title="title", article="big article"),
            orm.Comment(id=1, author="test1", body="body", parent_comment_id=0, nesting_level=0, post_id=1),
            orm.Comment(id=2, author="test2", body="reply 1", parent_comment_id=1, nesting_level=1, post_id=1),
            orm.Comment(id=3, author="test3", body="reply 2", parent_comment_id=1, nesting_level=1, post_id=1),
        ])

    async with session_factory() as session:
        async with session.begin():
            fixtures()

    result = await client.get("/api/v1/comment/children", query_string={"parent_comment_id": 1})
    data = result.json()
    assert result.status_code == 200
    assert data[0]["id"] == 2 and data[1]["id"] == 3
    assert data[0]["parent_comment_id"] == 1 and data[1]["parent_comment_id"] == 1
    assert data[0]["nesting_level"] == 1 and data[1]["nesting_level"] == 1
    assert data[0]["author"] == "test2" and data[1]["author"] == "test3"
    assert data[0]["body"] == "reply 1" and data[1]["body"] == "reply 2"


async def test_comment_children_empty(client: TestClient) -> None:
    result = await client.get("/api/v1/comment/children", query_string={"parent_comment_id": 1})
    assert result.status_code == 200
    assert len(result.json()) == 0
