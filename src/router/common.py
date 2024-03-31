import re
from typing import Annotated, Literal

from bs4 import BeautifulSoup
from fastapi import APIRouter, Security
from pydantic import BaseModel, Field

from src.router.account import User, get_current_active_user
from src.utils.api import api
from src.utils.markdown import MarkdownConverter

common_router = APIRouter(prefix='/common', tags=['Common'])


@common_router.post('/oss/upload')
async def oss_upload(
    user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return "ok"


class CrawlModel(BaseModel):
    source_url: str
    id: str = Field(description="用于索引的id，初始化为source_url")
    raw_html: str | None = None
    content_md: str | None = None
    platform: Literal["default", "wechat-article"] = "default"


@common_router.get(
    '/spider/crawl',
    response_model=CrawlModel
)
async def crawl_page(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    url: str
):
    response_model = CrawlModel(source_url=url, id=url)
    
    raw_html = api.get(url).text
    # response_model.raw_html = raw_html
    
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    m_wechat_article = re.search("mp.weixin.qq.com/s/(.*?)(?:\?|$)", url)
    if m_wechat_article:
        response_model.id = m_wechat_article.groups()[0]
        response_model.platform = "wechat-article"
        content_html = str(soup.select_one("#page-content"))
        # logger.info(content_html)
        if content_html:
            response_model.content_md = MarkdownConverter().convert(content_html)
    
    return response_model
