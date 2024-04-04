import re
from typing import Annotated

from fastapi import APIRouter, Security

from packages.common_fastapi.error_handler import error_handler
from src.router.account import User, get_current_active_user

common_router = APIRouter(prefix='/common', tags=['Common'])


@common_router.post('/oss/upload')
@error_handler
async def oss_upload(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return "ok"


def is_wechat_url(url: str):
    return re.search("mp.weixin.qq.com/s/(.*?)(?:\?|$)", url) is not None
