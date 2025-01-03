import json
from typing import Optional, Dict, Any

import requests
from fastapi import APIRouter, Header

from router.uni_pusher.types import Twitter

router = APIRouter(prefix='/jike')

BASE_URL = "https://web-api.okjike.com/api/graphql"


class JikePushContent(Twitter):
    submitToTopic: Optional[str] = None
    syncToPersonalUpdate: bool = True


@router.post("/content")
async def api_graphql(
    content: JikePushContent,

    custom_cookie: Optional[str] = Header(""),

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
        "priority": priority, }

    # Remove None values from headers
    headers = {k: v for k, v in headers.items() if v is not None}
    print(f"headers: {headers}")

    try:
        # Add common headers
        headers.update({
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"})

        # Send POST request
        request_data = {
            'operationName': 'CreateMessage',
            'variables': {
                'message': {
                    'content': content.text,
                    'syncToPersonalUpdate': content.syncToPersonalUpdate,
                    'submitToTopic': content.submitToTopic,
                    'pictureKeys': []}},
            'query': 'mutation CreateMessage($message: CreateMessageInput!) { createMessage(input: $message) { success toast __typename } } '},
        response = requests.post(BASE_URL, headers=headers, json=request_data, verify=True)
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
            "response_text": getattr(e.response, "text", None)}
