import fastapi
from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter(prefix='/jike')

BASE_URL = "https://web-api.okjike.com/api/graphql"


@router.post("/push")
async def api_graphql(
    text: str,
    custom_cookie: Optional[str] = Header(
        "_ga=GA1.2.1329611284.1728629767; fetchRankedUpdate=1730736532039; _gid=GA1.2.1224935922.1730736532; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiakZ6UG5obFd5UHI4QnE1VDBpTStiRFdQbkNcLzA2a0ZhVFpKajR6amlUU3kyejNlOVo5WFducUlYdFlrRE9nc0U5Y2VYK1wvVzFmREtCOXZrYmFnZDY0Z1NhWVh4TmRrODhzNzdMdXNHU2VcL2RYT3E2WU5rZ0sweVJIVTBnQk5cL215NW9DXC8xSWVEZDFJU3ZFTFNcL1BJMnNUUDk3Q3ozTkFKQXBGNGsySVhQS2I1R28wa2R5K0pkRkRCUzRkUjFFZ2ZMajNUV3JJclJHK3huNlQxV1pQMGpSM0tJdUU5bFZ1VHo5aDB5NnNzcjdoeFJhWTZDb1E1RWxwTUJ3WTZ2UmdrdkVWNkdhTHV4Uk9yZ2FJcTdGR0UxcENsN3ppcU5XV1V0cTg0UkFjc3B2U3F0VWJWdmM0MTB5Vk1vK3BtXC9JTkFOTVBZZDNTSUdISkpHUTV0czNwU0RUeE9kOHBTZnhXOWJPTHNlMWdnNGIrST0iLCJ2IjozLCJpdiI6InVEazgxXC9XbFN1cVwvSVVvMEVPY1MrZz09IiwiaWF0IjoxNzMwNzc5MzgyLjk0OX0.gZ4XJeSp1wFVmimI5-wOcNKfVfCqKxovuvDO0SPhmwE; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiM0FkUFpEOXY1Snh5cGNhM0xxVVkrYU1QSmV4OWlFbmpSY3YxM2lSUUU2Wk9Sbit1SXZEcmFXUXZpMmk5TlJMOTBweFRFOUgxZkFuOTFxS204TG5kWlwveWlqazY1bVRTWjk0MHZZQ2RqcEZ0bGNRNFJJam00czA1cG1BQlFlOGgwdGtsbjU1YVFIWWdEek92RXg0ckhsQWRsTUt6bUp2RFk4ZUhGelFMclZhQT0iLCJ2IjozLCJpdiI6IjNsT1ZjTGpkUjFGZWthcnAwMmFCZlE9PSIsImlhdCI6MTczMDc3OTM4Mi45NDl9.6CUNTCinTRTMNA7vrtnC_kIWnyCH3cN6UW6Nm3uq0Nw; _ga_LQ23DKJDEL=GS1.2.1730780456.9.0.1730780456.60.0.0; _gat=1"),

    sec_ch_ua_platform: Optional[str] = Header(""),
    user_agent: Optional[str] = Header(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
    accept: Optional[str] = Header("*/*"),
    sec_ch_ua: Optional[str] = Header(""),
    content_type: Optional[str] = Header("application/json"),
    dnt: Optional[str] = Header("1"),
    sec_ch_ua_mobile: Optional[str] = Header("?0"),
    origin: Optional[str] = Header("https://web.okjike.com"),
    sec_fetch_site: Optional[str] = Header("same-site"),
    sec_fetch_mode: Optional[str] = Header("cors"),
    sec_fetch_dest: Optional[str] = Header("empty"),
    accept_language: Optional[str] = Header("en-US,en;q=0.9"),
    priority: Optional[str] = Header("u=1, i")
) -> Dict[str, Any] | list:
    """
    Route generated from curl command
    Original URL: https://web-api.okjike.com/api/graphql
    Method: POST
    """

    # Construct headers
    headers = {
        "Cookie": custom_cookie,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "user-agent": user_agent,
        "accept": accept,
        "sec-ch-ua": sec_ch_ua,
        "content-type": content_type,
        "dnt": dnt,
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "origin": origin,
        "sec-fetch-site": sec_fetch_site,
        "sec-fetch-mode": sec_fetch_mode,
        "sec-fetch-dest": sec_fetch_dest,
        "accept-language": accept_language,
        "priority": priority,
    }

    # Remove None values from headers
    headers = {k: v for k, v in headers.items() if v is not None}

    try:
        # Add common headers
        headers.update({
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        })

        # Send POST request
        request_data = {
            'operationName': 'CreateMessage',
            'variables': {
                'message': {
                    'content': text,
                    'syncToPersonalUpdate': True,
                    'submitToTopic': '59747bef311d650011d5ab09',
                    'pictureKeys': []}},
            'query': 'mutation CreateMessage($message: CreateMessageInput!) { createMessage(input: $message) { success toast __typename } } '},
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=request_data,
            verify=True
        )
        # Check response status
        response.raise_for_status()

        # Try to parse JSON response
        try:
            return response.json()
        except (json.JSONDecodeError):
            return {"response": response.text}

    except (requests.exceptions.RequestException,) as e:
        return {
            "error": str(e),
            "status_code": getattr(e.response, "status_code", None),
            "response_text": getattr(e.response, "text", None)
        }
