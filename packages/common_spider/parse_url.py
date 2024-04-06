import re
from datetime import datetime
from typing import Optional, Literal

from bs4 import BeautifulSoup
from loguru import logger

from packages.common_api.index import api
from packages.common_llm.call_agent import call_agent
from packages.common_markdown.html2md import html2md
from packages.common_spider.schema import ICard, ISummary, PlatformType, IUserBasic, IImage
from src.schema import ModelType
from src.utils import check_platform_type


def parse_url(
    url: str,
    with_summary: Optional[bool] = False,
    md_with_img: Optional[bool] = False
) -> ICard:
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
    logger.info(f'content_md: {content_md}')
    
    content_summary: ISummary | None = None
    logger.info(f'-- summarizing content ({with_summary})')
    if with_summary:
        model: ModelType = "gpt-4"
        result = call_agent(content_md, "summarize-content", model)
        content_summary = ISummary(modelType=model, result=result)
        logger.info("-- summarized")
    
    platform_type: PlatformType = check_platform_type(url)
    card = ICard(
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
    logger.info(f"-- parsed: {card}")
    return card


if __name__ == '__main__':
    parse_url('http://mp.weixin.qq.com/s?__biz=MzI4NTgxMDk1NA==&amp;mid=2247490896&amp;idx=2&amp;sn=568f4c0a22313f5269f9fada94206ef4&amp;chksm=ebe7d535dc905c2308bdb321218da67ffe8a0fd32b63ef4bf6ecd706c43f86a12824dc329406&amp;mpshare=1&amp;scene=1&amp;srcid=0404tbqm2VUZRS72SUkVwq94&amp;sharer_shareinfo=481652bc83d18c4898309e7f413e6bae&amp;sharer_shareinfo_first=ae44e63fe8de9e05a5b6d5dfef67ce2c#rd')
