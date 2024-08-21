from fastapi import APIRouter

from src.router.account import account_router
from src.router.llm import llm_router
from src.router.oss import oss_router
from src.router.spider import spider_router
from src.router.vpn import vpn_router

root_router = APIRouter()

root_router.include_router(account_router)
root_router.include_router(llm_router)
root_router.include_router(spider_router)
root_router.include_router(oss_router)
root_router.include_router(vpn_router)

# wechaty 启动需要 py<3.11, 并且 开启 localhost:9001
# from src.router.wechat import wechat_router
# root_router.include_router(wechat_router)
