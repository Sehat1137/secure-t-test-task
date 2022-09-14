from typing import Union, List

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, status, Depends
from fastapi.responses import Response

from models import dto
from services import CommentService
from tools.container import Container


@inject
async def get_comments(
        post_id: int,
        nesting_level: int,
        comment_svc: CommentService = Depends(Provide[Container.comment_service])
) -> Union[Response, list[dto.GetCommentsResponse]]:
    comments = await comment_svc.get_comments(post_id, nesting_level)
    if comments is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return comments


@inject
async def create_comment(
        request: dto.CreateCommentRequest,
        comment_svc: CommentService = Depends(Provide[Container.comment_service])
) -> Response:
    result = await comment_svc.create_comment(request)
    if result.status:
        return Response(status_code=status.HTTP_201_CREATED)
    return Response(content=result.reason, status_code=status.HTTP_404_NOT_FOUND)


@inject
async def update_comment(
        request: dto.UpdateCommentRequest,
        comment_svc: CommentService = Depends(Provide[Container.comment_service])
) -> Response:
    result = await comment_svc.update_comment(request)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_404_NOT_FOUND)


@inject
async def remove_comment(
        id: int,
        comment_svc: CommentService = Depends(Provide[Container.comment_service])
) -> Response:
    result = await comment_svc.delete_comment(id)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(content="Comment not found, maybe it already been deleted", status_code=status.HTTP_404_NOT_FOUND)


@inject
async def get_child_comments(
        parent_comment_id: int,
        comment_svc: CommentService = Depends(Provide[Container.comment_service])
) -> list[dto.GetCommentsResponse]:
    return await comment_svc.get_children(parent_comment_id)


def get_router() -> APIRouter:
    router = APIRouter(prefix="/comment", tags=["comment"])
    router.add_api_route(
        "/fetch",
        get_comments,
        methods={"GET", },
        response_model=List[dto.GetCommentsResponse]

    )
    router.add_api_route("/create", create_comment, methods={"POST", }, status_code=status.HTTP_201_CREATED)
    router.add_api_route("/update", update_comment, methods={"PUT", }, status_code=status.HTTP_204_NO_CONTENT)
    router.add_api_route("/remove", remove_comment, methods={"DELETE", }, status_code=status.HTTP_204_NO_CONTENT)
    router.add_api_route(
        "/children",
        get_child_comments,
        methods={"GET", },
        response_model=List[dto.GetCommentsResponse]
    )
    return router
