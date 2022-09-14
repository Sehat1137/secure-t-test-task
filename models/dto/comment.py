from datetime import datetime
from typing import Optional

from pydantic import Field

from base import PydanticBaseModel

MIN_AUTHOR_LENGTH: int = 1
MAX_AUTHOR_LENGTH: int = 128

MIN_BODY_LENGTH: int = 1
MAX_BODY_LENGTH: int = 496


class GetCommentsResponse(PydanticBaseModel):
    id: int
    author: str = Field(min_length=MIN_AUTHOR_LENGTH, max_length=MAX_AUTHOR_LENGTH)
    body: str = Field(min_length=MIN_BODY_LENGTH, max_length=MAX_BODY_LENGTH)
    is_deleted: bool
    parent_comment_id: int
    nesting_level: int
    created_date: datetime
    updated_date: Optional[datetime]
    post_id: int


class CreateCommentRequest(PydanticBaseModel):
    author: str = Field(min_length=MIN_AUTHOR_LENGTH, max_length=MAX_AUTHOR_LENGTH)
    body: str = Field(min_length=MIN_BODY_LENGTH, max_length=MAX_BODY_LENGTH)
    parent_comment_id: int = Field(ge=0, default=0)
    post_id: int


class UpdateCommentRequest(PydanticBaseModel):
    id: int
    new_body: str = Field(min_length=MIN_BODY_LENGTH, max_length=MAX_BODY_LENGTH)


class CreateCommentStatus(PydanticBaseModel):
    status: bool
    reason: Optional[str]
