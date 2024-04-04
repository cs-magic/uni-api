import asyncio
import os
import re
from typing import Union, Literal, Optional

import dotenv
from loguru import logger
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from wechaty_grpc.wechaty.puppet import MessageType

from packages.common_datetime.utils import get_current_timestamp
from packages.common_wechat.patches.filebox import FileBox

dotenv.load_dotenv()

for k, v in os.environ.items():
    if "wechaty" in k.lower():
        print(k, "-->", v)

from wechaty import Wechaty, Message, Room, Contact


class WechatMessageUrlModel(BaseModel):
    type: Literal["wxmp-article", "wxmp-video", "default"] = "default"
    url: Optional[str] = None
    raw: Optional[str] = None


def parse_first_url(input: str):
    m = re.search(r"https?://[^\s，。]+|www\.[^\s，。]+", input)
    output = m[0] if m else None
    logger.debug(f"-- parsed first url: (Input={input}, Output={output})", )
    return output


def parse_url_from_wechat_message(msg: Message) -> WechatMessageUrlModel:
    text = msg.text()
    model = WechatMessageUrlModel(raw=text)
    
    type = msg.type()
    if type == MessageType.MESSAGE_TYPE_URL:
        m = re.search(r'<url>(.*?)</url>', text)
        if m:
            url = m[1]
            model.url = url
            if url:
                if re.search('mp.weixin.qq.com', url):
                    model.type = "wxmp-article"
    logger.info(f"parsed msg url model: {model}")
    return model


class MyBot(Wechaty):
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
        
        if room_name:
            if re.search(r'CS魔法社|test', room_name):
                logger.debug(f"<< Room(name={room_name}), Sender(name={sender_name}), Message(type={type}, text={text}), ")
                
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
                        driver.get('http://localhost:3000/card/gen')  # todo: conditional
                        
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
    asyncio.run(MyBot().start())
