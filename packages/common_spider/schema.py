from datetime import datetime
from typing import Literal

from packages.common_general.pydantic import BaseModel


class IUserBasic(BaseModel):
    id: str | None = None
    name: str | None = None
    avatar: str | None = None


class IImage(BaseModel):
    url: str
    width: str | None = None
    height: str | None = None


PlatformType = Literal["wxmpArticle", "xhsNote", "bilibiliVideo", "unknown"]


class ISummary(BaseModel):
    modelType: str
    result: str


class ICard(BaseModel):
    platformId: str
    platformType: PlatformType
    sourceUrl: str
    author: IUserBasic
    time: datetime
    title: str
    cover: IImage
    description: str
    contentMd: str
    contentSummary: ISummary | None
