
from fastapi import APIRouter, Header, Body
from typing import Optional, Dict, Any
import requests
import json
from .types import PusherContent

router = APIRouter(prefix='/jike')

BASE_URL = "https://web-api.okjike.com/api/graphql"


@router.post("/push")
async def api_graphql(
    content: PusherContent,

    custom_cookie: Optional[str] = Header(
        "_ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; fetchRankedUpdate=1730811992418; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiWVBSc2FpUjZOZTc2NU9XK3hXdTV2dm5tZXBQendwR2lDazVpajRaZVlBSDJSa0FVN2llSmZcL1hZZWZ5dzNNb0lGMng5MXBmWUs0djFTcmZTZEJ4MGdmdVhRVk01MmRqNGQzZWpiQUFDZVkxOXVSZjdaRWRTM1A4YjBaMTBUc1ZxS2xDaXJlWk9jeUJcL0toaWVLY0VZY3NTcTBkWTdxT01nYjRyQXBIY0xCa2hSXC9NaU80bHdqY1UyYUo3alVjTWU5cjBxR28wQzk0d1QyRk8yalRId2NxOWNVNG9EU3pTRUYwQ2RMNU54RkVXTXRBQ0M2MHZzeXk3bDN1UTRvSkJcL0QzMStSQkhYb1VHeTBzcGRJTllEanp2dzVQc1U0eTNObWRLYjJPZVNMOW9ZdnRCRlM5ZEJpbWFvVCtrRDdlOHNXXC9FMCswQXBwTW8zUVgyZEVyOFI1TVdJTmd3Y09yS2RvVk1pcjBQZmxTaXc9IiwidiI6MywiaXYiOiJlSWU4dHlabERxS0IxU2dzdlFjc2V3PT0iLCJpYXQiOjE3MzA4MjAwNjMuNDcxfQ.a2SywrTLsOitMMZvs8Em49kV7AWQYGzTL2KSl7yva1g; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiQ2lJOEI3djBwTkVqYXBBeHB5QXZ2S1wvVHVJdkpWYVBGb2FLb2dQZHlFNDFoU0YzWFYyVEloVkdwTHJNa3NWR05DRHY0MmlCNVVSNlwvZUlqcFFMM3VWUCt4dDlGZ1pYWGJUSWNPbDVFd1h3bTB0ektXTWgwMG5XcThuUWdMOFdITXBlUVFzdWtJSEtZdSthWURTQms1K2ErNXhLbHBtYUF0VE40UERKcDBpOXM9IiwidiI6MywiaXYiOiJKUDQ3R1g4YUVsN3h6SCtHZUc1NHNBPT0iLCJpYXQiOjE3MzA4MjAwNjMuNDcxfQ.3vK76b5a0LOjU4CUs7HyPMYQPH0nNjzDEdBbdkevQ-E; _gat=1; _ga_LQ23DKJDEL=GS1.2.1730818883.11.1.1730820133.60.0.0"),

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
    print(f"headers: {headers}")

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
                    'content': content.text,
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
