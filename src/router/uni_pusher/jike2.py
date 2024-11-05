from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://web-api.okjike.com/api/graphql"

@router.post("/api/graphql")
async def api_graphql(
    request_data: Dict[str, Any] = {'operationName': 'CreateMessage', 'variables': {'message': {'content': 't003', 'syncToPersonalUpdate': True, 'pictureKeys': []}}, 'query': 'mutation CreateMessage($message: CreateMessageInput!) { createMessage(input: $message) { success toast __typename } } '},
    cookie: Optional[str] = Header("_ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiNklUelVZS3NyUGZkRDU3SG9YZnZSbmh4dHlSWVpLYzNXRkdDMmZ2dWowbHdYTUlPUm9rRHJTQXorV1VMXC9vSGxLdTREVm9NZWNsdVpaSXVVSWZja09RZW1nVThONHpWSWd1NEZUSTFOcldvK3lvb3FiYXFPT0Q4UWFIQTJPXC9XZGRlQ1dSZFdkc2NqTzh6XC9OdDVnVzBSUWpzbDlCK05FdGZQYkkxT0lUUldkTk1DTmdYTnFRN09sV0xPQU9Sa1duZnZiT0Q1c2pQdUw0TERROVQ3dFN6aDlcL0tYTVRHMUlSd3BicWVJditKdmU1Uk5nQ284a1F1SE9VT2JNZjh1alpIV1lYRW9JSkgwRmRLdlpsNkc4bHV0OHpqWjkwZ2dmbEJrdEl2a0VPeGpHWjFIMnN2ejN3OG5LRUpqeWxZN1hwclNwKzZZOGRkMTk2QU83N0I3SzZWdFJham14Yk15S1Q1Qk5kMGtBZ0pndz0iLCJ2IjozLCJpdiI6IlFkWCtvUWRXbEs2bXBoMGR2SEtsUFE9PSIsImlhdCI6MTczMDgxMDg0OS45NDh9.ee9mF570ggkOTWaq4IbdWiHItS9PHwvjFAtJLgdHDEc; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiWlRKWTNBSkNPOHNVZkNQeEtcL2FXVmFaNDdmVDFCeWhNZDBTT0RVcXhiMVoyRU43aUFGMDRqZUI4dlZmMHh4a1N6U0lTamtkSHc4bG5PZFdFUG9SUXZqNkNBVVMwWkdSME16UStoalZRcWU2ekpjRE5MTnF1dnQzMytKOVkxWGlBZXlRTGhhdjRFTFdMV2RKN0daNzBOZXBKUzVPTUFZU09KRDZJOTE0ditGST0iLCJ2IjozLCJpdiI6ImFDYnJMbjRVVVpiMExQd0ZnejkzMlE9PSIsImlhdCI6MTczMDgxMDg0OS45NDh9.IOTmRf5M4hTuh87w5ALzWQ_HD0pECpFhG6O-WmOURrE; _ga_LQ23DKJDEL=GS1.2.1730811764.10.1.1730811991.60.0.0; fetchRankedUpdate=1730811992418"),
    sec_ch_ua_platform: Optional[str] = Header(""),
    user_agent: Optional[str] = Header("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
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
) -> Dict[str, Any]:
    """
    Route generated from curl command
    Original URL: https://web-api.okjike.com/api/graphql
    Method: POST
    """
    # Construct headers
    headers = {
        "Cookie": cookie,
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
        except json.JSONDecodeError:
            return {"response": response.text}
            
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": getattr(e.response, "status_code", None),
            "response_text": getattr(e.response, "text", None)
        }

