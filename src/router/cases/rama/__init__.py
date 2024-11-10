from fastapi import APIRouter

from .lofter import lofter_router
from .pixiv import pixiv_router

rama_router = APIRouter(prefix='/rama', tags=['Rama Case'])
rama_router.include_router(lofter_router)
rama_router.include_router(pixiv_router)
