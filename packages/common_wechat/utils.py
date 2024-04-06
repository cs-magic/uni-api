import os
import re

from loguru import logger
from wechaty import Message
from wechaty_grpc.wechaty.puppet import MessageType

from packages.common_wechat.schema import WechatMessageUrlModel
from settings import settings


def is_wechat_url(url: str):
    return re.search(r"mp.weixin.qq.com", url) is not None


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


def init_wechaty_envs():
    os.environ['WECHATY_PUPPET'] = settings.WECHATY_PUPPET
    os.environ['WECHATY_PUPPET_SERVICE_ENDPOINT'] = settings.WECHATY_PUPPET_SERVICE_ENDPOINT
    os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = settings.WECHATY_PUPPET_SERVICE_TOKEN
    for k, v in os.environ.items():
        if "wechaty" in k.lower():
            print(k, "-->", v)
