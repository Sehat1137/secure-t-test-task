from typing import Optional, Union

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, status, Depends
from fastapi.responses import Response

from models import dto
from services import PostService
from tools.container import Container


@inject
async def get_post(
        id: int,
        post_svc: PostService = Depends(Provide[Container.post_service])
) -> Union[Response, dto.GetPostResponse]:
    result: Optional[dto.GetPostResponse] = await post_svc.get_post(id)
    if not result:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return result


async def create_post(
        request: dto.CreatePostRequest,
        post_svc: PostService = Depends(Provide[Container.post_service])
) -> Response:
    await post_svc.create_post(request)
    return Response(status_code=status.HTTP_201_CREATED)


async def update_post(
        request: dto.UpdatePostRequest,
        post_svc: PostService = Depends(Provide[Container.post_service])
) -> Response:
    res = await post_svc.update_post(request)
    if not res:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def remove_post(
        id: int,
        post_svc: PostService = Depends(Provide[Container.post_service])
) -> Response:
    res = await post_svc.delete_post(id)
    if not res:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def get_router() -> APIRouter:
    router = APIRouter(prefix="/post", tags=["post"],)
    router.add_api_route(
        "",
        get_post,
        methods={"GET", },
        response_model=dto.GetPostResponse
    )
    router.add_api_route("/create", create_post, methods={"POST", })
    router.add_api_route("/update", update_post, methods={"PUT", })
    router.add_api_route("/remove", remove_post, methods={"DELETE", })
    return router
