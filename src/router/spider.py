from fastapi import APIRouter

from packages.common_fastapi.error_handler import error_handler
from packages.common_spider.parse_url import parse_url
from packages.common_spider.schema import ArticleModel

spider_router = APIRouter(prefix="/spider", tags=["Spider"])


@spider_router.get(
    '/crawl',
    response_model=ArticleModel
)
@error_handler
async def parse_url_route(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    url: str
):
    return parse_url(url)
