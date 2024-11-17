from fastapi import APIRouter

from router.uni_pusher.platforms.jike_api import jike_router
from router.uni_pusher.v1.zsxq_get_profile import zsxq_get_profile_router
from router.uni_pusher.v1.zsxq_post_content import zsxq_post_content_router

uni_pusher_router = APIRouter(prefix='/uni-pusher', tags=['uni-pusher'])

uni_pusher_router.include_router(jike_router)

uni_pusher_router.include_router(zsxq_post_content_router)
uni_pusher_router.include_router(zsxq_get_profile_router)
