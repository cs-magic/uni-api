import asyncio
import os
from typing import Union

import dotenv

dotenv.load_dotenv()

for k, v in os.environ.items():
    if "wechaty" in k.lower():
        print(k, "-->", v)

from wechaty import Wechaty, Message, Room, Contact
from wechaty_puppet import FileBox


class MyBot(Wechaty):
    async def on_message(self, msg: Message):
        from_contact = msg.talker()
        text = msg.text()
        room = msg.room()
        if text == 'ding':
            conversation: Union[Room, Contact] \
                = from_contact if room is None else room
            await conversation.ready()
            await conversation.say('dong')
            file_box = FileBox.from_url(
                'https://t7.baidu.com/it/u=1595072465,3644073269&fm=193&f=GIF',
                name='ding-dong.jpg')
            await conversation.say(file_box)


if __name__ == '__main__':
    asyncio.run(MyBot().start())
