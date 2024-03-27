from typing import Annotated

from fastapi import APIRouter, Security

from src.router.account import User, get_current_active_user

common_router = APIRouter(prefix='/common', tags=['Common'])


@common_router.post('/oss/upload')
async def oss_upload(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return "ok"
