from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://api.ruguoapp.com/1.0/users/profile"

@router.get("/jike/profile")
async def jike_profile(
    custom_cookie = Header(""),
    x_jike_access_token: Optional[str] = Header(""),
    x_jike_refresh_token: Optional[str] = Header(""),

    sec_ch_ua_platform: Optional[str] = Header(""),
    sec_ch_ua: Optional[str] = Header(""),
    sec_ch_ua_mobile: Optional[str] = Header("?0"),
    app_version: Optional[str] = Header("7.27.0"),
    user_agent: Optional[str] = Header("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
    accept: Optional[str] = Header("application/json, text/plain, */*"),
    dnt: Optional[str] = Header("1"),
    origin: Optional[str] = Header("https://web.okjike.com"),
    sec_fetch_site: Optional[str] = Header("cross-site"),
    sec_fetch_mode: Optional[str] = Header("cors"),
    sec_fetch_dest: Optional[str] = Header("empty"),
    referer: Optional[str] = Header("https://web.okjike.com/"),
    accept_language: Optional[str] = Header("en-US,en;q=0.9"),
    priority: Optional[str] = Header("u=1, i")
) -> Dict[str, Any]:
    """
    Route generated from curl command
    Original URL: https://api.ruguoapp.com/1.0/users/profile
    Method: GET
    """

    if custom_cookie:
        cookie = dict(k.split("=", 1) for k in custom_cookie.split("; "))
        x_jike_access_token = cookie.get("x_jike_access_token")
        x_jike_refresh_token = cookie.get("x_jike_refresh_token")

    # Construct headers
    headers = {
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "x-jike-refresh-token": x_jike_refresh_token,
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "app-version": app_version,
        "user-agent": user_agent,
        "accept": accept,
        "x-jike-access-token": x_jike_access_token,
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
    print(f"headers: {headers}")
    
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

