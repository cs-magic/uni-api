import asyncio
import json
import re
import time
from typing import Union

import yaml
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from wechaty import Message, Room, Contact
from wechaty_grpc.wechaty.puppet import MessageType

from packages.common_common.format_duration import format_duration
from packages.common_spider.parse_url import parse_url
from packages.common_wechat.bot.base import BaseWechatyBot
from packages.common_wechat.utils import parse_url_from_wechat_message
from settings import settings
from src.path import GENERATED_PATH, PROJECT_PATH
from packages.common_wechat.bot.schema import BotStatus, BotSettings
from packages.common_llm.schema import ModelType
from packages.common_wechat.bot.simulate_card_2 import Simulator


class UniParserBot(BaseWechatyBot):
    
    def __init__(self):
        super().__init__()
        self.dir = GENERATED_PATH
        self.simulator: Simulator | None = None
        self.started_time = time.time()
        self.normal_commands = ['help', 'ding', 'status']
        self.super_commands = ['shelp', "start", "stop", "enable-llm", "disable-llm", "refresh-driver-page",
                               "set-summary-model"]
        self.version = "0.5.0"
        self.features_enabled = True
        self.summary_model: ModelType | None = None
    
    @property
    def status(self):
        return BotStatus(
            version=self.version,
            features_enabled=self.features_enabled,
            summary_model=self.summary_model,
            alive_time=format_duration(time.time() - self.started_time),
        )
    
    @property
    def settings(self) -> BotSettings:
        env = Environment(loader=FileSystemLoader(PROJECT_PATH))
        template = env.get_template('bot.yml')
        rendered_yaml = yaml.safe_load(template.render(self.status.dict()))
        # logger.info(f"-- rendered yaml: {rendered_yaml}")
        return BotSettings.parse_obj(rendered_yaml)
    
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
            is_granted = "南川" in sender_name
            sender_avatar = sender.payload.avatar
            
            room = msg.room()
            
            conversation: Union[Room, Contact] = sender if room is None else room
            
            # await conversation.ready()
            
            # logger.debug(f"<< Room(name={room_name}), Sender(id={sender.contact_id}, name={sender_name}), Message(type={type}, text={text}), ")
            
            m_normal_command = re.match(f'({"|".join(self.normal_commands)})(?: |$)', text)
            if m_normal_command:
                command = m_normal_command[1]
                if command == 'ding':
                    await conversation.say('dong')
                elif command == "help":
                    await conversation.say(settings.bot.help)
                elif command == 'status':
                    await conversation.say(self.settings.status)
                return
            
            m_super_command = re.match(f'({"|".join(self.super_commands)})(?: |$)', text)
            if m_super_command and is_granted:
                command = m_super_command[1]
                if command == "shelp":
                    await conversation.say(settings.bot.shelp)
                else:
                    if command == "start":
                        self.features_enabled = True
                    elif command == "stop":
                        self.features_enabled = False
                    elif command == "enable-llm":
                        self.summary_model = True
                    elif command == "disable-llm":
                        self.summary_model = False
                    elif command == "refresh-driver-page":
                        self.simulator.driver.refresh()
                        await conversation.say("ok")
                    elif command == "set-summary-model":
                        await conversation.say("todo set")
                        return
                    await conversation.say("ok")
                return
            
            if not self.status.features_enabled:
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
                            async def simulate_card():
                                try:
                                    res = parse_url(url_model.url, self.status.summary_model)
                                    content = res.json()
                                    self._validate_content(content)
                                    if self.simulator is None:
                                        self.simulator = Simulator(self.dir)
                                    fb = self.simulator.run(content, sender_name, sender_avatar)
                                    await conversation.say(fb)
                                except Exception as e:
                                    await conversation.say(f"failed to generate card, reason: {e}")
                            
                            await simulate_card()
        
        except Exception as e:
            logger.error(e)
            await self.self().say(f"error: {e}")


uni_parser_bot = UniParserBot()

if __name__ == '__main__':
    asyncio.run(uni_parser_bot.start())
