import re
from pprint import pprint
from typing import List

from packages.common_common.pydantic import BaseModel


class ArticleSummaryModel(BaseModel):
    title: str | None
    description: str | None
    mindmap: str | None
    comment: str | None
    tags: List[str] | None


def parse_summary(content: str) -> ArticleSummaryModel:
    def parse_line(key: str):
        pattern = re.compile(fr'<{key}>(.*?)</{key}>', re.DOTALL)
        m = pattern.search(content)
        return m[1] if m else None
    
    tags_content = parse_line("tags")
    return ArticleSummaryModel(
        title=parse_line("title"),
        description=parse_line("description"),
        mindmap=parse_line("mindmap"),
        comment=parse_line("comment"),
        tags=[re.sub(r"\s+", "", i) for i in re.split(r'[,，]', tags_content)] if tags_content else None
    )


if __name__ == '__main__':
    data = parse_summary('''<title>中国高铁因报价过低被排除出保加利亚招标</title>\n<description>中国中车青岛四方公司因报价过低被排除出保加利亚高铁项目招标。欧盟认为中国中车集团获得巨额补贴，以低价抢占欧洲高铁订单。然而，中国中车集团的补贴并非专门针对保加利亚项目，而是整个集团的补贴。中国高铁的低价竞标策略引发了争议。</description>\n<mindmap>\n- 中国中车青岛四方公司被排除出保加利亚高铁项目招标\n  - 欧盟认为中国中车集团获得巨额补贴，以低价抢占欧洲高铁订单\n  - 补贴并非专门针对保加利亚项目，而是整个集团的补贴\n- 中国高铁的低价竞标策略引发争议\n  - 中国高铁以半价竞标，可能导致亏损\n  - 中国高铁的低价竞标策略被认为不符合市场规律\n  - 中国高铁的低价竞标策略被认为是贱卖高科技产品\n- 中国高铁的出海战略\n  - 高铁只是敲门砖，代表中国顶尖的基建技术\n  - 高铁项目可能亏损，但可以带动其他中国工业制品的出口\n  - 欧盟排挤中国高铁，是一种贸易保护主义\n</mindmap>\n<comment>中国高铁的低价竞标策略引发了争议，这不仅是因为可能导致亏损，也因为被认为是贱卖高科技产品。然而，这种策略也是中国高铁出海战略的一部分，通过高铁项目带动其他中国工业制品的出口。欧盟的排挤行为实际上是一种贸易保护主义。</comment>\n<tags>中国高铁, 保加利亚招标, 低价竞标</tags>''')
    pprint(data.dict())
