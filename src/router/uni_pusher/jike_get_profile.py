from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://api.ruguoapp.com/1.0/users/profile"

@router.get("/jike/profile")
async def jike_profile(
    sec_ch_ua_platform: Optional[str] = Header(""),
    x_jike_refresh_token: Optional[str] = Header("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiazVva1VQXC8zTTNpOUliQmpZOFFjdU5cL2xqMGpmMElETGhpOEJBZkl6ZFYxR3lWZ2RmWWxcL2llaHhQbDl3TGRPK0h3dVZkWUdqVm1oMFJMOWUwdVJxYkFBR3Z5YWRXYzFnZTE0dmFZNThhR0U1ZVE3Nk54a1NPT3F4R3VETmFVVXEzblRMN3hSRFhtbEVyN1dNOWVpY2hhWnptNmoybHg1UkxGSWV3d1czR20wPSIsInYiOjMsIml2Ijoia25ldTk4K01POTh6NzFEdDc4VlpEUT09IiwiaWF0IjoxNzMwOTAzMDA5LjE1Nn0.fs9VRliivfhHepsDX9rFtsGhwrPXedIfh53ebGPvDxU"),
    sec_ch_ua: Optional[str] = Header(""),
    sec_ch_ua_mobile: Optional[str] = Header("?0"),
    app_version: Optional[str] = Header("7.27.0"),
    user_agent: Optional[str] = Header("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
    accept: Optional[str] = Header("application/json, text/plain, */*"),
    x_jike_access_token: Optional[str] = Header("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiOWI2bTNNMFZ5TU9BZDFtaEFGeEVUOGxsZFlIYlwvZUk0Qk13d25QcU1nY2tHRTUyZ0h6T2xnREUrOE1VTmlVQUpkNWJ3ZkJpYmU3V0IrYlFhczlRMDJNVEtRSW51WGhXbjJHUGxwTm8reFRhbnUyTlpwVFRsVVFcL1piSzdZbjZFYU1aZGVRYk9EU1llMG5ibGZaK0JEZmp6Tk5YVG5RclVcL2toM01MUXZqQnp6XC9zeFpwUjZVa2xzbWphRGdTM0pneWRNXC9Gc2V2NDVvNGRPZHc0M2ptOXFmb2VJRUtUVHV4dERQRk81cU5ZR1JQZXdEbEZrYjZkbjZwXC9yVm1sNmZ6dmQ0V2ZHOCtMUHNnZXN4c29ocUdFQmdEa2s5S1JEQTJ6N3ZsSElaMU9QM21vU1VTNzdJazFVTVVYQmFnUno0WTM0enRjRmFaUGlvSmQ1R085VitpVW5jZUN5VzcwY3lYUG5oWTJJREpGRTdjPSIsInYiOjMsIml2IjoiMzBPY3FENVRaSGlvOUtqd3p0TlpiQT09IiwiaWF0IjoxNzMwOTAzMDA5LjE1Nn0.sKqVFu5iGDa-XhVn-5jDgrJ902cG1-LcRoFd-ztldhw"),
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

