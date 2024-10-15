from fastapi import APIRouter, Query
from typing import List
from datetime import date

from .src.ruc.query import query_ruc_badminton_court_info
from .src.types import BadmintonCourtStatus
from .src.tsinghua.query import query_tsinghua_badminton, TsinghuaBadmintonGym
from .src.beike.query import query_beike_badminton

badminton_router = APIRouter()

from enum import Enum
from typing import Literal


GymLiteral = Literal["北科大体育馆", "清华大学气膜馆", "清华大学综合体育馆", "清华大学西区体育馆", "人大羽毛球主馆"]

@badminton_router.get("/badminton", response_model=List[BadmintonCourtStatus], tags=["Badminton"])
async def get_badminton_status(
    gym: GymLiteral = Query(..., description="体育场名称"),
    date: date = Query(..., description="查询日期")
):
    date_str = date.strftime("%Y-%m-%d")

    if gym == "北科大体育馆":
        return query_beike_badminton(date_str)
    elif gym == "清华大学气膜馆":
        return query_tsinghua_badminton(date_str, TsinghuaBadmintonGym.清华大学气膜馆羽毛球场)
    elif gym == "清华大学综合体育馆":
        return query_tsinghua_badminton(date_str, TsinghuaBadmintonGym.清华大学综体羽毛球场)
    elif gym == "清华大学西区体育馆":
        return query_tsinghua_badminton(date_str, TsinghuaBadmintonGym.清华大学西体羽毛球场)
    elif gym == "人大羽毛球主馆":
        return query_ruc_badminton_court_info(date_str)
    else:
        raise ValueError(f"不支持的体育场: {gym}")
