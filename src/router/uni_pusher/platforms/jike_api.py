from typing import List, Optional

from fastapi import Depends, APIRouter, Form, UploadFile, File

from packages.common_fastapi.standard_error import standard_error_handler
from packages.common_fastapi.upload_file import convert_to_upload_file_info
from src.router.uni_pusher.platforms.jike_sdk import JikeSession, JikeSDK, JikeAuth
from src.router.uni_pusher.types import Twitter, Topic


async def get_headers(headers: JikeSession = Depends()) -> JikeSession:
    return headers


jike_router = APIRouter(prefix='/jike', tags=['即刻'])

jike_auth_router = APIRouter(prefix='/auth')


@jike_auth_router.post('/get-verify-code')
@standard_error_handler()
async def get_verify_code(phone_number: str, phone_area="+86"):
    return JikeAuth().get_verify_code(phone_number, phone_area)


@jike_auth_router.post('/verify-code')
@standard_error_handler()
async def verify_code(phone_number: str, phone_area="+86", *, code: str):
    return JikeAuth().verify_code(phone_number, phone_area, code)


@jike_auth_router.post('/refresh-token')
@standard_error_handler()
async def refresh_token(refresh_token: str):
    return JikeAuth().refresh_token(refresh_token)


jike_router.include_router(jike_auth_router)

jike_rss_router = APIRouter(prefix='/rss')


@jike_rss_router.post('/check')
@standard_error_handler()
async def check_rss(headers: JikeSession = Depends(get_headers)):
    return JikeSDK(headers).check_rss()


jike_router.include_router(jike_rss_router)


@jike_router.get('/profile')
@standard_error_handler()
async def read_profile(headers: JikeSession = Depends(get_headers)):
    return JikeSDK(headers).read_profile()


@jike_router.post('/search-topics')
@standard_error_handler()
async def search_topics(keywords: str, headers: JikeSession = Depends(get_headers)) -> List[Topic]:
    return JikeSDK(headers).search_topics(keywords)


@jike_router.post('/twitter')
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

    twitter: Twitter = Twitter(text=text, topic=topic, images=upload_file_infos, location=location, )
    print("twitter: ", twitter)
    return JikeSDK(headers).post_twitter(twitter)
