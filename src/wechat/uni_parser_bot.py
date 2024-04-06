import asyncio
import re
from typing import Union
from urllib.request import pathname2url

from loguru import logger
from wechaty import Message, Room, Contact
from wechaty_grpc.wechaty.puppet import MessageType

from packages.common_wechat.bot.base import BaseWechatyBot
from packages.common_wechat.patches.filebox import FileBox
from packages.common_wechat.utils import parse_url_from_wechat_message
from src.path import PROJECT_PATH, GENERATED_PATH
from src.router.spider import parse_url
from src.wechat.simulate_card_2 import Simulator


class UniParserBot(BaseWechatyBot):
    enabled = True
    
    def __init__(self):
        super().__init__()
        self.dir = GENERATED_PATH
        self.simulator = Simulator(self.dir)
    
    # how to write here with a @error_handler
    async def on_message(self, msg: Message):
        
        sender = msg.talker()
        sender_avatar = sender.payload.avatar
        
        sender_name = sender.name
        room = msg.room()
        
        await room.ready()
        room_name = await room.topic()
        conversation: Union[Room, Contact] = sender if room is None else room
        text = msg.text()
        type = msg.type()
        
        # logger.debug(f"<< Room(name={room_name}), Sender(id={sender.contact_id}, name={sender_name}), Message(type={type}, text={text}), ")
        
        if text == 'ding':
            await conversation.say('dong')
            return
        
        if text.startswith("/help"):
            with open(PROJECT_PATH.joinpath("help.md")) as f:
                await conversation.say(f.read())
            return
        
        granted = "南川" in sender_name
        if text.startswith("/stop"):
            if granted:
                self.enabled = False
                await conversation.say("stopped")
            else:
                await conversation.say("对不起，您暂无权限，请联系南川开通")
            return
        
        if text.startswith("/start"):
            if granted:
                self.enabled = True
                await conversation.say("started")
            else:
                await conversation.say("对不起，您暂无权限，请联系南川开通")
            return
        
        if not self.enabled:
            return
        
        async def send_parsed_card(content: str = None):
            if not content:
                logger.info('ignored since no content')
                return
            fn = self.simulator.run(content)
            if fn:
                logger.info(f"sending fn={fn}")
                # 本地文件，对文件名有要求，建议不要有 @_-+ 等符号
                await conversation.say(FileBox.from_file(self.dir.joinpath(fn).as_posix(), fn))
                logger.info("sent")
        
        if room_name:
            # group_regex = r'CS魔法社|test'
            group_regex = r'test'
            if re.search(group_regex, room_name):
                if text == "DING":
                    await conversation.say("DONG")
                
                elif type == MessageType.MESSAGE_TYPE_URL:
                    url_model = parse_url_from_wechat_message(msg)
                    
                    if not url_model.url:
                        logger.warning(f"url type of {msg} failed to parse any url")
                        return
                    
                    if (
                        url_model.type == "wxmp-article"  # todo: more types
                    ):
                        res = await parse_url(url_model.url, True)
                        await send_parsed_card(res.json())
                else:
                    await send_parsed_card(text)


uni_parser_bot = UniParserBot()

if __name__ == '__main__':
    asyncio.run(UniParserBot().start())
