from datetime import datetime
from typing import List

from pydantic import BaseModel


class UserBasicModel(BaseModel):
    name: str | None = None
    avatar: str | None = None


class ImageModel(BaseModel):
    url: str
    width: str | None = None
    height: str | None = None


class PlatformModel(BaseModel):
    id: str
    type: str
    name: str


class ArticleSummaryModel(BaseModel):
    title: str | None
    description: str | None
    mindmap: str | None
    comment: str | None
    tags: List[str] | None


class ArticleModel(BaseModel):
    platform: PlatformModel
    author: UserBasicModel
    time: datetime
    title: str
    cover: ImageModel
    description: str
    content_md: str
    content_summary: ArticleSummaryModel | None
