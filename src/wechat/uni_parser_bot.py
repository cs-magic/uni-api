import asyncio
import re
from typing import Union

from loguru import logger
from wechaty import Message, Room, Contact
from wechaty_grpc.wechaty.puppet import MessageType

from packages.common_spider.simulate_card import simulate_card
from packages.common_wechat.bot.base import BaseWechatyBot
from packages.common_wechat.patches.filebox import FileBox
from packages.common_wechat.utils import parse_url_from_wechat_message
from src.path import PROJECT_PATH


class UniParserBot(BaseWechatyBot):
    enabled = True
    
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
        
        logger.debug(f"<< Room(name={room_name}), Sender(id={sender.contact_id}, name={sender_name}), Message(type={type}, text={text}), ")
        logger.debug("<< Message: ", msg.payload)
        logger.debug("<< Sender: ", sender.payload)
        
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
        
        if room_name:
            if re.search(r'CS魔法社|test', room_name):
                if type == MessageType.MESSAGE_TYPE_URL:
                    url_model = parse_url_from_wechat_message(msg)
                    
                    if not url_model.url:
                        logger.warning(f"url type of {msg} failed to parse any url")
                        return
                    
                    if (
                        url_model.type == "wxmp-article"  # todo: more types
                    ):
                        data = simulate_card(url_model.url, sender_name, sender_avatar)
                        if data:
                            logger.info("-- sending")
                            await conversation.say(FileBox.from_url(data["url"], data["name"]))
                            logger.info("-- sent")
                
                if text == "DING":
                    await conversation.say("DONG")


uni_parser_bot = UniParserBot()

if __name__ == '__main__':
    asyncio.run(UniParserBot().start())
