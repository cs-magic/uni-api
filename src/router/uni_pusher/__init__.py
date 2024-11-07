from fastapi import APIRouter

from .jike_post_content import router as jike_post_content_router
from .jike_read_profile import router as jike_get_profile_router
from .jike_search import router as jike_search_router
from .jike_search_quanzi import router as jike_search_quanzi_router
from .jike_upload_image import jike_upload_image_route
from .jike_upload_image_access_token import jike_upload_image_access_token_route

from .zsxq_post_content import router as zsxq_post_content_router
from .zsxq_get_profile import router as zsxq_get_profile_router

uni_pusher_router = APIRouter(prefix='/uni-pusher', tags=['uni-pusher'])

uni_pusher_router.include_router(jike_post_content_router)
uni_pusher_router.include_router(jike_get_profile_router)
uni_pusher_router.include_router(jike_search_router)
uni_pusher_router.include_router(jike_search_quanzi_router)
uni_pusher_router.include_router(jike_upload_image_access_token_route)
uni_pusher_router.include_router(jike_upload_image_route)

uni_pusher_router.include_router(zsxq_post_content_router)
uni_pusher_router.include_router(zsxq_get_profile_router)