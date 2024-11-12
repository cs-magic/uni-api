from packages.spider.schema import PlatformType
from packages.wechat.utils import is_wechat_url


def check_platform_type(url: str) -> PlatformType:
    if is_wechat_url(url):
        return "wxmpArticle"
    else:
        return "unknown"
