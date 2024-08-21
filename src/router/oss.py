from typing import Annotated

from fastapi import Security, APIRouter

from packages.common_fastapi.error_handler import error_handler
from src.router.account import User, get_current_active_user

oss_router = APIRouter(prefix='/oss', tags=["OSS"])


@oss_router.post('/upload')
@error_handler
async def upload_oss(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return "ok"
