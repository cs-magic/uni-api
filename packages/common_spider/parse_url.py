import json
import re
from datetime import datetime
from typing import Optional, Literal

from bs4 import BeautifulSoup
from loguru import logger

from packages.common_api.index import api
from packages.common_llm.agent.call_agent import call_agent
from packages.common_markdown.html2md import html2md
from packages.common_spider.schema import ICard, ISummary, PlatformType, IUserBasic, IImage
from src.path import GENERATED_PATH
from packages.common_llm.schema import ModelType
from src.utils import check_platform_type


def parse_url(
    url: str,
    summary_model: Optional[ModelType] = None,
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
    # logger.info(f'content_md: {content_md}')
    
    platform_type: PlatformType = check_platform_type(url)
    platform_id = re.search(r'sn=(.*?)&', parse_meta("og:url", "property"))[1]
    
    content_summary: ISummary | None = None
    logger.info(f'-- summarizing content (model={summary_model})')
    if summary_model:
        result = call_agent(content_md, "summarize-content", summary_model)
        content_summary = ISummary(modelType=summary_model, result=result)
        
        # mock
        # content_summary = ISummary.parse_obj({"modelType": "gpt-4", "result": "<title>Kimi在3月份实现双端爆发，月活超字节豆包</title>\n<description>月之暗面在3月份实现了爆发式增长，移动端月活超过百万，超越字节豆包，网页端月访问超过千万，实现了3倍的增长。</description>\n<mindmap>\n- Kimi获得新一轮投资\n  - 投资方包括阿里、美团等\n  - 投资金额达10亿美元\n- 3月份Kimi实现双端爆发\n  - 移动端月活超百万\n  - 网页端月访问超千万\n- Kimi月活超越字节豆包\n- 网页端月访问实现3倍增长\n</mindmap>\n<comment>Kimi在新一轮投资的推动下，实现了在移动端和网页端的爆发式增长，表现出强大的市场竞争力。</comment>\n<tags>投资,用户增长,市场竞争力</tags>"})
        # with open(GENERATED_PATH.joinpath(f"{platform_type}-{platform_id}.summary.json"), "w") as f:
        #     json.dump(content_summary.dict(), f, ensure_ascii=False)
        logger.info("-- summarized")
    
    card = ICard(
        sourceUrl=url,
        platformId=platform_id,
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
    with open(GENERATED_PATH.joinpath(f"{platform_type}-{platform_id}.card.json"), 'w') as f:
        json.dump(card.dict(), f, ensure_ascii=False)
    return card


if __name__ == '__main__':
    url = 'http://mp.weixin.qq.com/s?__biz=MzI4NTgxMDk1NA==&amp;mid=2247490896&amp;idx=2&amp;sn=568f4c0a22313f5269f9fada94206ef4&amp;chksm=ebe7d535dc905c2308bdb321218da67ffe8a0fd32b63ef4bf6ecd706c43f86a12824dc329406&amp;mpshare=1&amp;scene=1&amp;srcid=0404tbqm2VUZRS72SUkVwq94&amp;sharer_shareinfo=481652bc83d18c4898309e7f413e6bae&amp;sharer_shareinfo_first=ae44e63fe8de9e05a5b6d5dfef67ce2c#rd'
    parse_url(url, None)
