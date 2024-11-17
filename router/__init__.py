from fastapi import APIRouter

from router.account import account_router
from router.cases import cases_router
from router.llm import llm_router
from router.map import map_router
from router.oss import oss_router
from router.spider import spider_router
from router.sport import sport_router
from router.uni_pusher import uni_pusher_router
from router.vpn import vpn_router
from router.wechat import wechat_route

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
