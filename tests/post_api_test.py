from contextlib import AbstractAsyncContextManager
from typing import Callable

import pytest
import sqlalchemy as sa
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import orm

pytestmark = pytest.mark.asyncio


async def test_post_get(
        client: TestClient,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
) -> None:

    def fixtures():
        session.add_all([
            orm.Post(id=1, title="title1", article="big article"),
            orm.Post(id=2, title="title2", article="big article"),
            orm.Post(id=3, title="title3", article="big article"),
            orm.Comment(author="some author", body="a", post_id=1),
            orm.Comment(author="some author", body="m", post_id=2),
            orm.Comment(author="some author", body="o", post_id=2),
            orm.Comment(author="some author", body="g", post_id=3),
            orm.Comment(author="some author", body="u", post_id=3),
            orm.Comment(author="some author", body="s", post_id=3),
        ])

    async with session_factory() as session:
        async with session.begin():
            fixtures()

    for id in range(1, 4):
        result = await client.get(f"/api/v1/post", query_string={"id": id})
        assert result.status_code == 200
        data = result.json()
        assert data["title"] == f"title{id}"
        assert data["count_of_comments"] == id


async def test_post_get_404(client: TestClient) -> None:
    result = await client.get(f"/api/v1/post", query_string={"id": 1})
    assert result.status_code == 404


async def test_post_create(
        client: TestClient,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
) -> None:
    result = await client.post("/api/v1/post/create", json={"title": "some title", "article": "some article"})
    assert result.status_code == 201
    async with session_factory() as session:
        post = await session.scalar(
            sa.select(orm.Post).where((orm.Post.title == "some title") & (orm.Post.article == "some article"))
        )
    assert post is not None


async def test_post_update(
        client: TestClient,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
) -> None:
    async with session_factory() as session:
        async with session.begin():
            session.add(orm.Post(id=1, title="title", article="small article"))

        result = await client.put(
            "/api/v1/post/update",
            json={"id": 1, "new_title": "Title", "new_article": "Big article"}
        )
        post = await session.get(orm.Post, 1)

    assert result.status_code == 204
    assert post.updated_date is not None
    assert post.title == "Title"
    assert post.article == "Big article"


async def test_post_update_404(client: TestClient):
    result = await client.put("/api/v1/post/update", json={"id": 1, "new_title": "Title", "new_article": "Big article"})
    assert result.status_code == 404


async def test_post_remove(
        client: TestClient,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
) -> None:
    async with session_factory() as session:
        async with session.begin():
            session.add(orm.Post(id=1, title="title", article="small article"))

        result = await client.delete("/api/v1/post/remove", query_string={"id": 1})
        post = await session.get(orm.Post, 1)
    assert result.status_code == 204
    assert post is None


async def test_post_remove_404(client: TestClient):
    result = await client.delete("/api/v1/post/remove", query_string={"id": 1})
    assert result.status_code == 404
