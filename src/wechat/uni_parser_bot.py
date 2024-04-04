import asyncio
import re
from typing import Union

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from wechaty import Message, Room, Contact
from wechaty_grpc.wechaty.puppet import MessageType

from packages.common_datetime.utils import get_current_timestamp
from packages.common_general.utils import parse_first_url
from packages.common_wechat.bot.base import BaseWechatyBot
from packages.common_wechat.patches.filebox import FileBox
from packages.common_wechat.utils import parse_url_from_wechat_message
from settings import settings


class UniParserBot(BaseWechatyBot):
    enabled = False
    
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
        
        if "南川" in sender_name:
            if text.startswith("/stop"):
                self.enabled = False
            elif text.startswith("/start"):
                self.enabled = True
            elif text.startswith("/help"):
                await conversation.say(f"""
                /start
                /stop
                /help
                """)
        
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
                        logger.debug("-- starting browser")
                        # todo: conditional
                        service = Service(ChromeDriverManager().install())
                        options = Options()
                        options.add_argument("--headless")
                        driver = webdriver.Chrome(service=service, options=options)
                        
                        logger.debug("-- visiting")
                        driver.get(f'{settings.FRONTEND_BASEURL}/card/gen')
                        
                        if sender_name:
                            logger.debug("-- filling user name")
                            driver.find_element(By.ID, "card-user-name").send_keys(sender_name)
                        
                        if sender_avatar:
                            logger.debug("-- filling user avatar")
                            driver.find_element(By.ID, "card-user-avatar").send_keys(sender_avatar)
                        
                        logger.debug("-- filling url")
                        driver.find_element(By.ID, "card-input-url").send_keys(url_model.url)
                        
                        logger.debug("-- clicking generate button")
                        driver.find_element(By.ID, "generate-card").click()
                        
                        logger.debug("-- waiting upload button")
                        WebDriverWait(driver, 30).until(
                            expected_conditions.element_to_be_clickable((By.ID, "upload-card"))
                        ).click()
                        
                        logger.debug("-- waiting uploaded result")
                        uploaded_tip = WebDriverWait(driver, 30).until(
                            expected_conditions.visibility_of_element_located((
                                By.CSS_SELECTOR, ".toaster div[data-title]"))
                        ).text
                        oss_url = parse_first_url(uploaded_tip)
                        if oss_url:
                            file_name = f"{get_current_timestamp(kind='s')}.png"
                            logger.info(f'sending Card(url={oss_url}, name={file_name})')
                            filebox = FileBox.from_url(oss_url, file_name)
                            await conversation.say(filebox)
                            logger.info("sent")
                        return
                
                if text == "DING":
                    await conversation.say("DONG")
        
        if text == 'ding':
            await conversation.say('dong')


if __name__ == '__main__':
    asyncio.run(UniParserBot().start())
