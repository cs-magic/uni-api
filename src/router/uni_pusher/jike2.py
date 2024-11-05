from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://web-api.okjike.com/api/graphql"

@router.post("/api/graphql")
async def api_graphql(
    request_data: Dict[str, Any] = {'operationName': 'CreateMessage', 'variables': {'message': {'content': 't003', 'syncToPersonalUpdate': True, 'pictureKeys': []}}, 'query': 'mutation CreateMessage($message: CreateMessageInput!) { createMessage(input: $message) { success toast __typename } } '},
    cookie: Optional[str] = Header("_ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; fetchRankedUpdate=1730811992418; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiNDN1bzdhaXhXWFc0VEpGbzBRbzhuNWhMeFlcL3dmQTBWY1lVNFJOQ0VOR1NTYU1XazJHXC9ycXhiZVFQOG4yNkVqUFwvc016S0FSNm8wOEJIWDVxWHY0UlV5NVwvU3YzeUZmSzBNRlJTV2dnTm5LNStPeVR5ZWFpM1JQWXZ4am43UnRYQW9Ec0FcL2hOeHVaRlFUOUk1V1lzaG1XZE5cLzY1VjlcL3BYWEhjbVhcL3FSRklYU3ppN05nc05Jdnc2K2IzT0w1SmwwN1NFSEV0TEN1Rm54Tm9DNGJTRXRLclN0YkMxRDFtN1djVzlRZ0c4NGFtN2hnOTUwaW9YNEdXOUZZSVBHTjNUdVdRUEdFditTWEhzZzhkQkgyY1BZUUU0c2M5dlhuenJDYVZCRkZGSnljdlpzMFNCMmQ4UUE0NTNYZ25MdVFXbEd6SXFiN2dDMGhjZSt4Q2hCU1wveWNDaFZScVg2RkpFMUxQT0J0MjZEZ0JZPSIsInYiOjMsIml2IjoidlZxTnpBa1NVV0huQ3p3aUpqMVA5Zz09IiwiaWF0IjoxNzMwODEzOTIxLjk2NX0.-7rGnwvOA9N6-XnWykqIvio218o6apJCscAI0icUNmA; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoidlN3YmZLeXRHY3RjMDFrNlFlV1gxWHlDQ2FGZ1RkVlBzZVBCUmZUOHIzUllHYVFJRGNZMWp3VUxCQnR1OFZndm9aUldBSHptVEpRb3M1VzhmSE92QXZvbW9HMHlZc2hkTlRsMDdsdVZ2ckVIdytDeW1zWUFTemlFSEhiTk9jelNGXC9taTR3dVduUWU4TU82YXpPWlF1YXJUaUphaUozcEZZV3JtWHRhS1NzYz0iLCJ2IjozLCJpdiI6IkFGRXVlWTIrdDZyRTBpb0xETjVPZUE9PSIsImlhdCI6MTczMDgxMzkyMS45NjV9.pAbdEittw6dcmKN848tmC1Vm7EYzynCbcAn3pYiey4o; _gat=1; _ga_LQ23DKJDEL=GS1.2.1730811764.10.1.1730814407.60.0.0"),
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
            verify=True,
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

