from fastapi import APIRouter

from src.router.wechat.official_account import wechat_official_account_route

wechat_route = APIRouter(prefix="/wechat", tags=["wechat"])
wechat_route.include_router(wechat_official_account_route)
