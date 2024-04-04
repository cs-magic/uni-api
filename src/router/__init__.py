from fastapi import APIRouter

from src.router.account import account_router
from src.router.agent import agent_router
from src.router.common import common_router
from src.router.llm import llm_router
from src.router.wechat import wechat_router

root_router = APIRouter()

root_router.include_router(account_router)
root_router.include_router(llm_router)
root_router.include_router(agent_router)
root_router.include_router(wechat_router)
root_router.include_router(common_router)
