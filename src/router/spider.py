import re
from datetime import datetime
from typing import Literal, Optional

from bs4 import BeautifulSoup
from fastapi import APIRouter
from loguru import logger

from packages.common_api.index import api
from packages.common_fastapi.error_handler import error_handler
from packages.common_markdown.html2md import html2md
from packages.common_spider.schema import ArticleModel, UserBasicModel, ImageModel, PlatformType
from packages.common_wechat.utils import is_wechat_url
from src.router.llm import call_agent

spider_router = APIRouter(prefix="/spider", tags=["Spider"])


@spider_router.get(
    '/parse-url',
    response_model=ArticleModel
)
@error_handler
async def parse_url_route(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    url: str,
    with_summary: Optional[bool] = False,
    md_with_img: Optional[bool] = False
):
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
    content_md = html2md(content_html, md_with_img)
    
    content_summary: str | None = None
    logger.info(f'-- summarizing content ({with_summary})')
    if with_summary:
        content_summary = await call_agent(content_md, "summarize-content", "gpt-4")
        logger.info("-- summarized")
    
    platform_type: PlatformType = check_platform_type(url)
    return ArticleModel(
        platformId=re.search(r'sn=(.*?)&', parse_meta("og:url", "property"))[1],
        platformType=platform_type,
        author=UserBasicModel(
            # id= # todo
            name=re.search(r'var nickname = htmlDecode\("(.*?)"\);', text)[1],
            avatar=re.search(r'var hd_head_img = "(.*?)"', text)[1],
        ),
        time=datetime.utcfromtimestamp(int(re.search(r'var ct = "(.*?)"', text)[1])),
        title=parse_meta("og:title", "property"),
        cover=ImageModel(
            url=parse_meta("og:image", "property"),
            width=None,
            height=None
        ),
        description=parse_meta("description", "name"),
        contentMd=content_md,
        contentSummary=content_summary,
    )


def check_platform_type(url: str) -> PlatformType:
    if is_wechat_url(url):
        return "wxmpArticle"
    else:
        return "unknown"

#
# def check_platform_type_2(url: str) -> PlatformType:
#     return "wxmpArticle" if is_wechat_url(url) else "unknown"
#
