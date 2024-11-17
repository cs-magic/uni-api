from fastapi import APIRouter

from .gaode import gaode_router
from .baidu import baidu_router
from .tencent import tencent_router

map_router = APIRouter(prefix="/map", tags=["Map"])

map_router.include_router(gaode_router, prefix="/gaode")
map_router.include_router(baidu_router, prefix="/baidu")
map_router.include_router(tencent_router, prefix="/tencent")

