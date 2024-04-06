from typing import Optional

from fastapi import APIRouter

from packages.common_fastapi.error_handler import error_handler
from packages.common_spider.parse_url import parse_url
from packages.common_spider.schema import ICard

spider_router = APIRouter(prefix="/spider", tags=["Spider"])


@spider_router.get(
    '/parse-url',
    response_model=ICard
)
@error_handler
async def parse_url_route(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    url: str,
    with_summary: Optional[bool] = False,
    md_with_img: Optional[bool] = False
):
    return parse_url(url, with_summary, md_with_img)
