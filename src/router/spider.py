from typing import Optional

from fastapi import APIRouter

from packages.fastapi.standard_error import standard_error_handler
from packages.llm.schema import ModelType
from packages.spider.parse_url import parse_url
from packages.spider.schema import ICard

spider_router = APIRouter(prefix="/spider", tags=["Spider"])


@spider_router.get('/parse-url', response_model=ICard)
@standard_error_handler()
async def parse_url_(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    url: str, summary_model: Optional[ModelType] = None, md_with_img: Optional[bool] = False
):
    return parse_url(url, summary_model, md_with_img)
