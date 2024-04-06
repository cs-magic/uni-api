import re
from datetime import datetime
from typing import Literal, Optional

from bs4 import BeautifulSoup
from fastapi import APIRouter
from loguru import logger

from packages.common_api.index import api
from packages.common_fastapi.error_handler import error_handler
from packages.common_markdown.html2md import html2md
from packages.common_spider.schema import IArticle, IUserBasic, IImage, PlatformType, ISummary
from src.router.llm import call_agent
from src.schema import ModelType
from src.utils import check_platform_type

spider_router = APIRouter(prefix="/spider", tags=["Spider"])


async def parse_url(
    url: str,
    with_summary: Optional[bool] = False,
    md_with_img: Optional[bool] = False
) -> IArticle:
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
    
    content_summary: ISummary | None = None
    logger.info(f'-- summarizing content ({with_summary})')
    if with_summary:
        model: ModelType = "gpt-4"
        result = await call_agent(content_md, "summarize-content", model)
        content_summary = ISummary(modelType=model, result=result)
        logger.info("-- summarized")
    
    platform_type: PlatformType = check_platform_type(url)
    return IArticle(
        platformId=re.search(r'sn=(.*?)&', parse_meta("og:url", "property"))[1],
        platformType=platform_type,
        author=IUserBasic(
            # id= # todo
            name=re.search(r'var nickname = htmlDecode\("(.*?)"\);', text)[1],
            avatar=re.search(r'var hd_head_img = "(.*?)"', text)[1],
        ),
        time=datetime.utcfromtimestamp(int(re.search(r'var ct = "(.*?)"', text)[1])),
        title=parse_meta("og:title", "property"),
        cover=IImage(
            url=parse_meta("og:image", "property"),
            width=None,
            height=None
        ),
        description=parse_meta("description", "name"),
        contentMd=content_md,
        contentSummary=content_summary,
    )


@spider_router.get(
    '/parse-url',
    response_model=IArticle
)
@error_handler
async def parse_url_route(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    url: str,
    with_summary: Optional[bool] = False,
    md_with_img: Optional[bool] = False
):
    return parse_url(url, with_summary, md_with_img)
