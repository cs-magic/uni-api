from typing import Optional, List

from fastapi import UploadFile, Form
from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    name: str
    avatar: str



class Twitter(BaseModel):
    text: Optional[str] = None
    topic: Optional[str] = None
    location: Optional[str] = None
    images: Optional[List[UploadFile]] = None


class PlatformBase:

    def read_profile(self) -> User:
        raise NotImplementedError()

    def push_twitter(self, twitter: Twitter):
        raise NotImplementedError()


class PlatfromSession(BaseModel):
    custom_cookie: Optional[str] = Field(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._cookie = None

        # 先试着从 custom_cookie 中解析
        if self.custom_cookie is not None:
            self._cookie = dict(k.split("=", 1) for k in self.custom_cookie.strip().split("; "))

        # 如果没有的话，则通过其他 headers 确定
        # 也有可能还不够，在继承类中补齐
        if not self._cookie:
            self._cookie = self.model_dump(by_alias=True, exclude={"custom_cookie"})
