import re
from datetime import datetime
from typing import Literal

from bs4 import BeautifulSoup
from loguru import logger

from packages.common_api.index import api
from packages.common_markdown.index import html2md
from packages.common_spider.schema import UserBasicModel, ImageModel, PlatformModel, ArticleModel
from packages.common_wechat.utils import is_wechat_url


def parse_url(url: str):
    logger.info(f"-- parsing url: {url}")
    text = api.get(url).text
    # logger.info(f"-- fetched content: {text}")
    
    soup = BeautifulSoup(text, "html.parser")
    
    def parse_meta(key: str, type: Literal['name', 'property']):
        meta = soup.find('meta', attrs={type: key})
        # logger.info(f"-- meta: type={type}, key={key}, meta={meta}")
        return meta.get("content")
    
    soup.find(id="meta_content").extract()  # remove author info
    content_html = str(soup.find(id="img-content"))
    content_md = html2md(content_html)
    
    return ArticleModel(
        platform=PlatformModel(
            id=re.search(r'sn=(.*?)&', parse_meta("og:url", "property"))[1],
            name=parse_meta("og:site_name", "property"),  # 微信公众平台
            type="wxmp-article" if is_wechat_url(url) else "unknown",
        ),
        author=UserBasicModel(
            name=re.search(r'var nickname = htmlDecode\("(.*?)"\);', text)[1],
            avatar=re.search(r'var hd_head_img = "(.*?)"', text)[1],
        ),
        cover=ImageModel(
            url=parse_meta("og:image", "property"),
            width=None,
            height=None
        ),
        title=parse_meta("og:title", "property"),
        description=parse_meta("description", "name"),
        content_md=content_md,
        time=datetime.utcfromtimestamp(int(re.search(r'var ct = "(.*?)"', text)[1])),
    
    )
