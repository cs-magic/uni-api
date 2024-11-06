from fastapi import APIRouter
from .jike_post_content import router as jike_post_content_router
from .jike_get_profile import router as jike_get_profile_router
from .zsxq_post_content import router as zsxq_post_content_router
from .zsxq_get_profile import router as zsxq_get_profile_router

uni_pusher_router = APIRouter(prefix='/uni-pusher', tags=['uni-pusher'])

uni_pusher_router.include_router(jike_post_content_router)
uni_pusher_router.include_router(jike_get_profile_router)
uni_pusher_router.include_router(zsxq_post_content_router)
uni_pusher_router.include_router(zsxq_get_profile_router)