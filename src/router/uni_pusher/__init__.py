from fastapi import APIRouter

from src.router.uni_pusher.platforms.jike import jike_route
from src.router.uni_pusher.v1.zsxq_get_profile import router as zsxq_get_profile_router
from src.router.uni_pusher.v1.zsxq_post_content import router as zsxq_post_content_router

uni_pusher_router = APIRouter(prefix='/uni-pusher', tags=['uni-pusher'])

uni_pusher_router.include_router(jike_route)

uni_pusher_router.include_router(zsxq_post_content_router)
uni_pusher_router.include_router(zsxq_get_profile_router)
