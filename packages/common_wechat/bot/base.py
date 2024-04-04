from wechaty import Wechaty

from packages.common_wechat.utils import init_wechaty_envs


class BaseWechatyBot(Wechaty):
    def __init__(self):
        init_wechaty_envs()
        super().__init__()
