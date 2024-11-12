from fastapi import APIRouter

from packages.fastapi.standard_error import standard_error_handler

oss_router = APIRouter(prefix='/oss', tags=["OSS"])


@oss_router.post('/upload')
@standard_error_handler()
async def upload_oss(# user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return "ok"
