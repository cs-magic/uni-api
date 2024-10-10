from fastapi import APIRouter, Query
from typing import Optional
import requests


rama_router = APIRouter(prefix='/rama', tags=['Rama'])

@rama_router.get("/pixiv/novels/search")
async def search_novels(
    word: str = Query(..., description="Search word"),
    order: str = Query("date_d", description="Order of results"),
    mode: str = Query("all", description="Search mode"),
    p: int = Query(1, description="Page number"),
    csw: int = Query(0, description="CSW parameter"),
    s_mode: str = Query("s_tag", description="Search mode"),
    gs: int = Query(0, description="GS parameter"),
    lang: str = Query("en", description="Language"),
    version: Optional[str] = Query(None, description="API version")
):

    params = {
        "word": word,
        "order": order,
        "mode": mode,
        "p": p,
        "csw": csw,
        "s_mode": s_mode,
        "gs": gs,
        "lang": lang,
    }
    if version:
        params["version"] = version

    response = requests.get(f"https://www.pixiv.net/ajax/search/novels/{word}", params=params)
    return response.json()