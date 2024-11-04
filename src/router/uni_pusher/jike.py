from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter(prefix='/jike')

BASE_URL = "https://web-api.okjike.com/api/graphql"

@router.post("/push")
async def api_graphql(
    text: str,
    cookie: Optional[str] = Header("_ga=GA1.2.1329611284.1728629767; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiWXloUlwvUXhQSXNIV1MrMzB0VjJjRHhzK3V4M2lMbUlhckhrdzNpdVwvRGpITUdCVXh3T3pjQ1hGaGlJNGlmTW9wdUZWNXo4disyVVdNNkt6TUNhUUg5UDJWUlh2T1M4U3RFSnlMcnlyTTNXeEliYVZrQWxzemxuQlRjeW9keUZJWFJpViszVXNFbkw3TUtFZHJsWnJkUTNQZjkzdTlDYVwvYnU1Y2xEZUFBbDIrNE9ZWXh5UWtEY1M2RllNOHhxM28wbUNrWGQzQ0tnc3ZzR0x3ajZlcXhcL3BkaVlKMURYNmhuTEJpeXo1eTVGWHpmTXhtVDQ5TjJoWjVjbit3RnZBSHJYSjc5QTh1TnJaa2diWWlBVGJQa1NhUHJRcmFUZXlwVzlCbnVPaEV0VVRuNVYxN3pRaVpvamF2aUEwU2NoRUdyQ0ZTTVdIWjB4SVArcHZ3Um5EbmVyeTdleE5WdnZ6UFVYUUtydUJcL2J6dU09IiwidiI6MywiaXYiOiJxczVmcHk3a0MyaE5EaFFkWk1qVTNBPT0iLCJpYXQiOjE3MzA3MzY1MjkuNTU3fQ.tmuTQ1E4WXdH6A8xJFJrngcSs2jKSuvIwZLuFnstPCA; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoib2toV1VTXC9kYkQ0ZzI1MXl3NU1VQjBcL3h3Y0VzRXdBZXREMEhFOTFWYXJhMW5QNGJMaXpUMVZxZmNqbk0rNm1pVjA4dldKMFIwYVJmNzVTeEVwRFR1eVgzdXV0SVwvQVRiWG03QVFvVVwveTlDalwvZlppYTd5aUJuU2poZGlLZmpWQ2dHVDdcL2VINjRLYmtOcWpGbTlyUE1OeWlHdHM4QkFKaW1sRElIV0xiQ1VVPSIsInYiOjMsIml2IjoiSFc3WW5wbmdGS2hWZDY2TmVQV1ZrUT09IiwiaWF0IjoxNzMwNzM2NTI5LjU1N30.O5yL2NdEG4ucKJc2_cVk98F3SVHH8xXiXoVitCTcZjo; fetchRankedUpdate=1730736532039; _gid=GA1.2.1224935922.1730736532; _ga_LQ23DKJDEL=GS1.2.1730736532.5.0.1730736532.60.0.0"),

) -> Dict[str, Any]:
    """
    Route generated from curl command
    Original URL: https://web-api.okjike.com/api/graphql
    Method: POST
    """

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
        request_data = {'operationName': 'CreateMessage', 'variables': {'message': {'content': text, 'syncToPersonalUpdate': True, 'submitToTopic': '59747bef311d650011d5ab09', 'pictureKeys': []}}, 'query': 'mutation CreateMessage($message: CreateMessageInput!) { createMessage(input: $message) { success toast __typename } } '},
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

