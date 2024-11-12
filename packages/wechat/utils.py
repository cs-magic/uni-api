import re


def is_wechat_url(url: str):
    return re.search(r"mp.weixin.qq.com", url) is not None


