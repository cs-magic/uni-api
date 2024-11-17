from fastapi import APIRouter

from router.wechat.official_account.article import wechat_official_account_route
wechat_route = APIRouter(prefix="/wechat", tags=["微信"])
wechat_route.include_router(wechat_official_account_route)
