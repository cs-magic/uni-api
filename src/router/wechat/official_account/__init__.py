from fastapi import APIRouter

from src.router.wechat.official_account.article import wechat_official_account_article_route
from src.router.wechat.official_account.lijigang_article import lijigang_route

wechat_official_account_route = APIRouter(prefix="/official_account", tags=["official_account"])
wechat_official_account_route.include_router(wechat_official_account_article_route)
wechat_official_account_route.include_router(lijigang_route)
