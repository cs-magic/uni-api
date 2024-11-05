from fastapi import APIRouter
from .jike import router as jike_router
from .zsxq import router as zsxq_router

uni_pusher_router = APIRouter(prefix='/uni-pusher', tags=['uni-pusher'])

uni_pusher_router.include_router(jike_router)
uni_pusher_router.include_router(zsxq_router)