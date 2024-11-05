
from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

from src.router.uni_pusher.types import PusherContent

router = APIRouter(prefix='/zsxq')

BASE_URL = "https://api.zsxq.com/v2/groups/51111828288514/topics"


@router.post("/push")
async def groups_51111828288514_topics(
    content: PusherContent,

    custom_cookie: Optional[str] = Header("zsxq_access_token=A1A047AB-483F-F2F6-27EF-831393870534_1E07900F500D3426; zsxqsessionid=7ea23150bf6824166e923cd620adf32d; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2228242851215251%22%2C%22first_id%22%3A%22192f0c0191d1983-0199f37f9d1c95c-1f525636-3686400-192f0c0191e2a46%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZjBjMDE5MWQxOTgzLTAxOTlmMzdmOWQxYzk1Yy0xZjUyNTYzNi0zNjg2NDAwLTE5MmYwYzAxOTFlMmE0NiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjI4MjQyODUxMjE1MjUxIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2228242851215251%22%7D%7D; abtest_env=product"),

    x_request_id: Optional[str] = Header("239dc4d1c-0679-f2cc-d21c-d3dcd822013"),
    x_version: Optional[str] = Header("2.64.0"),
    x_timestamp: Optional[str] = Header("1730731549"),
    x_signature: Optional[str] = Header("90500d7ba435ab968bf0193996b27ff68e4850c2"),

    referer: Optional[str] = Header("https://wx.zsxq.com/"),

    sec_ch_ua_platform: Optional[str] = Header(""),
    sec_ch_ua: Optional[str] = Header(""),
    user_agent: Optional[str] = Header(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
    accept: Optional[str] = Header("application/json, text/plain, */*"),
    dnt: Optional[str] = Header("1"),
    content_type: Optional[str] = Header("application/json"),
    origin: Optional[str] = Header("https://wx.zsxq.com"),
    sec_ch_ua_mobile: Optional[str] = Header("?0"),
    sec_fetch_site: Optional[str] = Header("same-site"),
    sec_fetch_mode: Optional[str] = Header("cors"),
    sec_fetch_dest: Optional[str] = Header("empty"),
    accept_language: Optional[str] = Header("en-US,en;q=0.9"),
    priority: Optional[str] = Header("u=1, i"),
) -> Dict[str, Any]:
    """
    Route generated from curl command
    Original URL: https://api.zsxq.com/v2/groups/51111828288514/topics
    Method: POST
    """


    # Construct headers
    headers = {
        "Cookie": custom_cookie,
        "x-request-id": x_request_id,
        "x-version": x_version,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "sec-ch-ua": sec_ch_ua,
        "x-timestamp": x_timestamp,
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "x-signature": x_signature,
        "user-agent": user_agent,
        "accept": accept,
        "dnt": dnt,
        "content-type": content_type,
        "origin": origin,
        "sec-fetch-site": sec_fetch_site,
        "sec-fetch-mode": sec_fetch_mode,
        "sec-fetch-dest": sec_fetch_dest,
        "referer": referer,
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
        request_data: Dict[str, Any] = {
            "req_data": {
                "mentioned_user_ids": [],
                "file_ids": [],
                "image_ids": [],
                "text": content.text + "\n",
                "type": "topic"
            }
        }
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=request_data,
            verify=True,
                # 'zsxq_access_token=A1A047AB-483F-F2F6-27EF-831393870534_1E07900F500D3426; zsxqsessionid=7ea23150bf6824166e923cd620adf32d; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2228242851215251%22%2C%22first_id%22%3A%22192f0c0191d1983-0199f37f9d1c95c-1f525636-3686400-192f0c0191e2a46%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZjBjMDE5MWQxOTgzLTAxOTlmMzdmOWQxYzk1Yy0xZjUyNTYzNi0zNjg2NDAwLTE5MmYwYzAxOTFlMmE0NiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjI4MjQyODUxMjE1MjUxIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2228242851215251%22%7D%7D; abtest_env=product'
            # cookies=dict(item.split("=", 1) for item in cookie.split("; "))
        )
        # Check response status
        response.raise_for_status()

        # Try to parse JSON response
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"response": response.text}

    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": getattr(e.response, "status_code", None),
            "response_text": getattr(e.response, "text", None)
        }

