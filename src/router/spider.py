from typing import Optional

from fastapi import APIRouter

from packages.common_fastapi.error_handler import error_handler
from packages.common_spider.parse_url import parse_url
from packages.common_spider.schema import ICard
from packages.common_llm.schema import ModelType

spider_router = APIRouter(prefix="/spider", tags=["Spider"])


@spider_router.get(
    '/parse-url',
    response_model=ICard
)
@error_handler
async def parse_url_route(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    url: str,
    summary_model: Optional[ModelType] = None,
    md_with_img: Optional[bool] = False
):
    return parse_url(url, summary_model, md_with_img)
