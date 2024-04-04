from fastapi import APIRouter, BackgroundTasks

from src.utils.error_handler import error_handler
from src.wechat.uni_parser_bot import bot

wechat_router = APIRouter(prefix="/wechat", tags=["WeChat"])


@wechat_router.post("/start")
@error_handler
async def start_wechat(bt: BackgroundTasks):
    # 写法参考：https://chat.openai.com/c/7fd97349-925e-49e5-ade1-f361fb936be8
    bt.add_task(bot.start)
    return {"message": "bot is starting"}


@wechat_router.post("/stop")
@error_handler
async def stop_wechat():
    await bot.stop()
    return {"message": "bot is stopping"}
