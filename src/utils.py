from packages.common_spider.schema import PlatformType
from packages.common_wechat.utils import is_wechat_url


def check_platform_type(url: str) -> PlatformType:
    if is_wechat_url(url):
        return "wxmpArticle"
    else:
        return "unknown"
