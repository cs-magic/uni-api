from fastapi import APIRouter

from src.router.account import account_router
from src.router.cases import cases_router
from src.router.llm import llm_router
from src.router.oss import oss_router
from src.router.spider import spider_router
from src.router.vpn import vpn_router
from src.router.uni_pusher import uni_pusher_router

from src.router.map import map_router
from src.router.sport import sport_router
from src.router.wechat import wechat_route

root_router = APIRouter()

root_router.include_router(account_router)
root_router.include_router(llm_router)
root_router.include_router(spider_router)
root_router.include_router(oss_router)
root_router.include_router(vpn_router)
root_router.include_router(sport_router)
root_router.include_router(map_router)
root_router.include_router(uni_pusher_router)
root_router.include_router(wechat_route)
root_router.include_router(cases_router)
