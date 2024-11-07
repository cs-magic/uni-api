from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://web-api.okjike.com/api/graphql"

@router.post("/jike/search/quanzi")
async def jike_search_quanzi(
    keywords: str,
    custom_cookie: Optional[str] = Header(""),

    accept: Optional[str] = Header("*/*"),
    accept_language: Optional[str] = Header("en-US,en;q=0.9"),
    content_type: Optional[str] = Header("application/json"),
    dnt: Optional[str] = Header("1"),
    origin: Optional[str] = Header("https://web.okjike.com"),
    priority: Optional[str] = Header("u=1, i"),
    sec_ch_ua: Optional[str] = Header(""),
    sec_ch_ua_mobile: Optional[str] = Header("?0"),
    sec_ch_ua_platform: Optional[str] = Header(""),
    sec_fetch_dest: Optional[str] = Header("empty"),
    sec_fetch_mode: Optional[str] = Header("cors"),
    sec_fetch_site: Optional[str] = Header("same-site"),
    user_agent: Optional[str] = Header("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
):
    """
    Route generated from curl command
    Original URL: https://web-api.okjike.com/api/graphql
    Method: POST
    """

    request_data: Dict[str, Any] = {'operationName': 'SearchTopics', 'variables': {'keywords': keywords}, 'query': 'query SearchTopics($keywords: String!) { search { topics(keywords: $keywords, onlyUserPostEnabled: true) { highlightWord { words singleMaxHighlightTime totalMaxHighlightTime __typename } nodes { id content briefIntro squarePicture { thumbnailUrl __typename } __typename } __typename } __typename } } '},

    # Construct headers
    headers = {
        "accept": accept,
        "accept-language": accept_language,
        "content-type": content_type,
        "cookie": custom_cookie,
        "dnt": dnt,
        "origin": origin,
        "priority": priority,
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": sec_ch_ua_mobile,
        "sec-ch-ua-platform": sec_ch_ua_platform,
        "sec-fetch-dest": sec_fetch_dest,
        "sec-fetch-mode": sec_fetch_mode,
        "sec-fetch-site": sec_fetch_site,
        "user-agent": user_agent,
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

        # Send POST request with request_data directly
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
