from typing import List, Optional

from fastapi import Depends, APIRouter, Form, UploadFile, File

from packages.common_fastapi.standard_error import standard_error_handler
from src.router.uni_pusher.platforms.jike_sdk import JikeSession, JikeSDK
from packages.common_fastapi.upload_file import convert_to_upload_file_info
from src.router.uni_pusher.types import Twitter, Topic


async def get_headers(headers: JikeSession = Depends()) -> JikeSession:
    return headers


jike_route = APIRouter(prefix='/jike', tags=['即刻'])


@jike_route.post('/auth/get-verify-code')
@standard_error_handler()
async def get_verify_code(phone_number: str, phone_area="+86"):
    return JikeSDK().get_verify_code(phone_number, phone_area)


@jike_route.post('/auth/verify-code')
@standard_error_handler()
async def verify_code(phone_number: str, phone_area="+86", *, code: str):
    return JikeSDK().verify_code(phone_number, phone_area, code)


@jike_route.get('/profile')
@standard_error_handler()
async def read_profile(headers: JikeSession = Depends(get_headers)):
    return JikeSDK(headers).read_profile()


@jike_route.post('/search-topics')
@standard_error_handler()
async def search_topics(keywords: str, headers: JikeSession = Depends(get_headers)) -> List[Topic]:
    return JikeSDK(headers).search_topics(keywords)


@jike_route.post('/twitter')
@standard_error_handler()
async def push_twitter(
    text: str = Form(None),
    topic: str = Form(None),
    location: str = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    headers: JikeSession = Depends(get_headers)
):
    # Convert FastAPI UploadFile list to UploadFileInfo list
    upload_file_infos = None
    if images:
        upload_file_infos = [await convert_to_upload_file_info(img) for img in images]
    
    twitter: Twitter = Twitter(
        text=text,
        topic=topic,
        images=upload_file_infos,
        location=location,
    )
    print("twitter: ", twitter)
    return JikeSDK(headers).push_twitter(twitter)


@jike_route.post('/notifications/check')
@standard_error_handler()
async def check_notifications(headers: JikeSession = Depends(get_headers)):
    return JikeSDK(headers).check_notifications()


@jike_route.post('/refresh-token')
@standard_error_handler()
async def refresh_token(refresh_token: str):
    return JikeSDK().refresh_token(refresh_token)
