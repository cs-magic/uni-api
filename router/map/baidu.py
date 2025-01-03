from fastapi import APIRouter, Query
from typing import Optional
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

baidu_router = APIRouter()

BAIDU_AK = os.getenv("BAIDU_MAP_AK")
BASE_URL = "https://api.map.baidu.com/reverse_geocoding/v3/"
GEOCODING_URL = "https://api.map.baidu.com/geocoding/v3/"

@baidu_router.get("/reverse_geocoding")
async def baidu_reverse_geocoding(
    location: str = Query(..., description="经纬度坐标"),
    coordtype: Optional[str] = Query("bd09ll", description="坐标类型"),
    ret_coordtype: Optional[str] = Query(None, description="返回的坐标类型"),
    extensions_poi: Optional[int] = Query(0, description="是否返回POI数据"),
    extensions_road: Optional[bool] = Query(False, description="是否返回道路数据"),
    radius: Optional[int] = Query(1000, description="POI召回半径"),
    output: Optional[str] = Query("json", description="输出格式"),
    language: Optional[str] = Query(None, description="返回结果语言"),
    language_auto: Optional[int] = Query(None, description="是否自动填充行政区划")
):
    params = {
        "ak": BAIDU_AK,
        "location": location,
        "coordtype": coordtype,
        "extensions_poi": extensions_poi,
        "output": output,
    }
    
    if ret_coordtype:
        params["ret_coordtype"] = ret_coordtype
    if extensions_road:
        params["extensions_road"] = "true"
    if radius != 1000:
        params["radius"] = radius
    if language:
        params["language"] = language
    if language_auto is not None:
        params["language_auto"] = language_auto

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        return response.json()

@baidu_router.get("/geocoding")
async def baidu_geocoding(
    address: str = Query(..., description="待解析的地址"),
    city: Optional[str] = Query(None, description="地址所在的城市名"),
    ret_coordtype: Optional[str] = Query(None, description="返回的坐标类型"),
    output: Optional[str] = Query("json", description="输出格式"),
    callback: Optional[str] = Query(None, description="回调函数名称"),
    extension_analys_level: Optional[int] = Query(None, description="是否触发解析到最小地址结构功能")
):
    params = {
        "ak": BAIDU_AK,
        "address": address,
        "output": output,
    }
    
    if city:
        params["city"] = city
    if ret_coordtype:
        params["ret_coordtype"] = ret_coordtype
    if callback:
        params["callback"] = callback
    if extension_analys_level is not None:
        params["extension_analys_level"] = extension_analys_level

    async with httpx.AsyncClient() as client:
        response = await client.get(GEOCODING_URL, params=params)
        return response.json()
