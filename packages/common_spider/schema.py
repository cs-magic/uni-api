from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class UserBasicModel(BaseModel):
    id: str | None = None
    name: str | None = None
    avatar: str | None = None


class ImageModel(BaseModel):
    url: str
    width: str | None = None
    height: str | None = None


PlatformType = Literal["wxmpArticle", "xhsNote", "bilibiliVideo", "unknown"]


class ArticleModel(BaseModel):
    platformId: str
    platformType: PlatformType
    author: UserBasicModel
    time: datetime
    title: str
    cover: ImageModel
    description: str
    contentMd: str
    contentSummary: str | None
