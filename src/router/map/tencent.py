from fastapi import APIRouter, Query
from typing import Optional
import httpx
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

tencent_router = APIRouter()

TENCENT_MAP_KEY = os.getenv("TENCENT_MAP_KEY")
print("TENCENT_MAP_KEY", TENCENT_MAP_KEY)

TENCENT_GEOCODER_URL = "https://apis.map.qq.com/ws/geocoder/v1/"

class GeocoderResponse(BaseModel):
    status: int
    message: str
    result: dict

@tencent_router.get("/geocoder", response_model=GeocoderResponse)
async def geocoder(
    address: str = Query(..., description="要解析获取坐标及相关信息的输入地址"),
    output: Optional[str] = Query("json", description="返回格式：支持JSON/JSONP，默认JSON"),
    callback: Optional[str] = Query(None, description="JSONP方式回调函数")
):
    params = {
        "key": TENCENT_MAP_KEY,
        "address": address,
        "output": output,
    }
    if callback:
        params["callback"] = callback

    async with httpx.AsyncClient() as client:
        response = await client.get(TENCENT_GEOCODER_URL, params=params)
        response.raise_for_status()
        return response.json()

