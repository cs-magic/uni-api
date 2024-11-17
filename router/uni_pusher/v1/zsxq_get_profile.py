from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

zsxq_get_profile_router = APIRouter()

BASE_URL = "https://api.zsxq.com/v3/users/self"

@zsxq_get_profile_router.get("/zsxq/profile")
async def zsxq_profile(
    custom_cookie: Optional[str] = Header(""),
    x_timestamp: Optional[str] = Header("1730907137"),
    x_request_id: Optional[str] = Header("dff4f1bc8-eb5f-4724-a28c-0e775b7fde0"),
    x_signature: Optional[str] = Header("965d4028443950d8942100b5f66ec350d9be3383"),
    x_version: Optional[str] = Header("2.65.0"),

    sec_ch_ua_platform: Optional[str] = Header(""),
    sec_ch_ua: Optional[str] = Header(""),
    sec_ch_ua_mobile: Optional[str] = Header("?0"),
    user_agent: Optional[str] = Header("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
    accept: Optional[str] = Header("application/json, text/plain, */*"),
    dnt: Optional[str] = Header("1"),
    origin: Optional[str] = Header("https://wx.zsxq.com"),
    sec_fetch_site: Optional[str] = Header("same-site"),
    sec_fetch_mode: Optional[str] = Header("cors"),
    sec_fetch_dest: Optional[str] = Header("empty"),
    referer: Optional[str] = Header("https://wx.zsxq.com/"),
    accept_language: Optional[str] = Header("en-US,en;q=0.9"),
    priority: Optional[str] = Header("u=1, i")
) -> Dict[str, Any]:
    """
    Route generated from curl command
    Original URL: https://api.zsxq.com/v3/users/self
    Method: GET
    """
    # Construct headers
    headers = {
        "Cookie": custom_cookie,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "x-request-id": x_request_id,
        "x-version": x_version,
        "sec-ch-ua": sec_ch_ua,
        "x-timestamp": x_timestamp,
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "x-signature": x_signature,
        "user-agent": user_agent,
        "accept": accept,
        "dnt": dnt,
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
    
    try:
        # Add common headers
        headers.update({
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        })
        # Send GET request
        response = requests.get(
            BASE_URL,
            headers=headers,
            verify=True
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

