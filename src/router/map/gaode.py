from fastapi import APIRouter, Query
from typing import Optional
import httpx
import os

import requests

gaode_router = APIRouter()

GAODE_API_KEY = os.getenv("GAODE_API_KEY")  # 请替换为您的高德 API Key
# print("GAODE_API_KEY", GAODE_API_KEY)
BASE_URL = "https://restapi.amap.com/v3/geocode"

@gaode_router.get("/geo")
async def geocode(
    address: str = Query(..., description="结构化地址信息"),
    city: Optional[str] = Query(None, description="指定查询的城市"),
    output: str = Query("JSON", description="返回数据格式类型"),
    callback: Optional[str] = Query(None, description="回调函数"),
):
    params = {
        "key": GAODE_API_KEY,
        "address": address,
        "output": output,
    }
    if city:
        params["city"] = city
    if callback:
        params["callback"] = callback

    
    response = requests.get(f"{BASE_URL}/geo", params=params)
    return response.json()

@gaode_router.get("/regeo")
async def reverse_geocode(
    location: str = Query(..., description="经纬度坐标"),
    poitype: Optional[str] = Query(None, description="返回附近POI类型"),
    radius: int = Query(1000, description="搜索半径"),
    extensions: str = Query("base", description="返回结果控制"),
    roadlevel: Optional[int] = Query(None, description="道路等级"),
    output: str = Query("JSON", description="返回数据格式类型"),
    callback: Optional[str] = Query(None, description="回调函数"),
    homeorcorp: int = Query(0, description="是否优化POI返回顺序"),
):
    params = {
        "key": GAODE_API_KEY,
        "location": location,
        "radius": radius,
        "extensions": extensions,
        "output": output,
        "homeorcorp": homeorcorp,
    }
    if poitype:
        params["poitype"] = poitype
    if roadlevel is not None:
        params["roadlevel"] = roadlevel
    if callback:
        params["callback"] = callback

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/regeo", params=params)
    return response.json()

