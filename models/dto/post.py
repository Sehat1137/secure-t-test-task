from datetime import datetime
from typing import Optional

from pydantic import Field

from base import PydanticBaseModel

TITLE_MAX_LENGTH: int = 248
TITLE_MIN_LENGTH: int = 1

ARTICLE_MAX_LENGTH: int = 5000
ARTICLE_MIN_LENGTH: int = 1


class GetPostResponse(PydanticBaseModel):
    id: int
    title: str
    created_date: datetime
    updated_date: Optional[datetime]
    count_of_comments: int


class CreatePostRequest(PydanticBaseModel):
    title: str = Field(min_length=TITLE_MIN_LENGTH, max_length=TITLE_MAX_LENGTH)
    article: str = Field(min_length=ARTICLE_MIN_LENGTH, max_length=ARTICLE_MAX_LENGTH)


class UpdatePostRequest(PydanticBaseModel):
    id: int
    new_title: Optional[str] = Field(min_length=TITLE_MIN_LENGTH, max_length=TITLE_MAX_LENGTH)
    new_article: Optional[str] = Field(min_length=ARTICLE_MIN_LENGTH, max_length=ARTICLE_MAX_LENGTH)
