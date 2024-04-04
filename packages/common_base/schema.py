from typing import TypedDict, Optional


class UserBasic(TypedDict):
    name: Optional[str]
    avatar: Optional[str]


class Dimension(TypedDict):
    width: Optional[int]
    height: Optional[int]


class Cover(TypedDict):
    url: str
    dimension: Optional[Dimension]
