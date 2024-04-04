from datetime import datetime

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


class ArticleModel(BaseModel):
    platform: PlatformModel
    cover: ImageModel
    author: UserBasicModel
    
    title: str
    description: str
    content_md: str
    time: datetime
