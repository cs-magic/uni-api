from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Form

from packages.common_fastapi.error_handler import error_handler
from packages.common_wechat.bot.uni_parser_bot import uni_parser_bot

wechat_router = APIRouter(prefix="/wechat", tags=["WeChat"])


@wechat_router.post("/start")
@error_handler
async def start_wechat(
    id: Annotated[str, Form()] = "default",
    *,
    bt: BackgroundTasks):
    # 写法参考：https://chat.openai.com/c/7fd97349-925e-49e5-ade1-f361fb936be8
    bt.add_task(uni_parser_bot.start)
    return {"message": "bot is starting"}


@wechat_router.post("/stop")
@error_handler
async def stop_wechat(
    id: Annotated[str, Form()] = "default",
):
    await uni_parser_bot.stop()
    return {"message": "bot is stopping"}
