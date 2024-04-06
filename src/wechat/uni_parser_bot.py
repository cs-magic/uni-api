import asyncio
import json
import re
from typing import Union

from loguru import logger
from wechaty import Message, Room, Contact
from wechaty_grpc.wechaty.puppet import MessageType

from packages.common_spider.parse_url import parse_url
from packages.common_wechat.bot.base import BaseWechatyBot
from packages.common_wechat.utils import parse_url_from_wechat_message
from src.path import PROJECT_PATH, GENERATED_PATH
from src.wechat.simulate_card_2 import Simulator


class UniParserBot(BaseWechatyBot):
    enabled = True
    
    def __init__(self):
        super().__init__()
        self.dir = GENERATED_PATH
        self.simulator = Simulator(self.dir)
    
    @staticmethod
    def _validate_content(content: str):
        try:
            logger.debug('-- validating json')
            item = json.loads(content)
            logger.debug('-- json validated')
            logger.debug('-- validating identity')
            _id = item['platformId']
            logger.debug('-- identity validated')
        except Exception as e:
            raise Exception(f"invalid content: {content}")
    
    # how to write here with a @error_handler
    async def on_message(self, msg: Message):
        try:
            type = msg.type()
            
            text = msg.text()
            
            sender = msg.talker()
            sender_name = sender.name
            granted = "南川" in sender_name
            sender_avatar = sender.payload.avatar
            
            room = msg.room()
            
            conversation: Union[Room, Contact] = sender if room is None else room
            
            # await conversation.ready()
            
            async def simulate_card(content: str):
                try:
                    self._validate_content(content)
                    fb = self.simulator.run(content, sender_name, sender_avatar)
                    await conversation.say(fb)
                except Exception as e:
                    await conversation.say(f"failed to generate card, reason: {e}")
            
            # logger.debug(f"<< Room(name={room_name}), Sender(id={sender.contact_id}, name={sender_name}), Message(type={type}, text={text}), ")
            
            if text == 'ding':
                await conversation.say('dong')
                return
            
            if text.startswith("/help"):
                with open(PROJECT_PATH.joinpath("help.md")) as f:
                    await conversation.say(f.read())
                return
            
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
            
            if text.startswith("/raw"):
                await simulate_card(text.split("/raw")[1])
            
            if not self.enabled:
                return
            
            if room:
                room_name = await room.topic()
                
                # group_regex = r'CS魔法社|test'
                group_regex = r'test'
                if re.search(group_regex, room_name):
                    if type == MessageType.MESSAGE_TYPE_URL:
                        url_model = parse_url_from_wechat_message(msg)
                        
                        if not url_model.url:
                            logger.warning(f"url type of {msg} failed to parse any url")
                            return
                        
                        if (
                            url_model.type == "wxmp-article"  # todo: more types
                        ):
                            res = parse_url(url_model.url, True)
                            await simulate_card(res.json())
 
        except Exception as e:
            logger.error(e)
            await self.self().say(f"error: {e}")


uni_parser_bot = UniParserBot()

if __name__ == '__main__':
    asyncio.run(UniParserBot().start())
