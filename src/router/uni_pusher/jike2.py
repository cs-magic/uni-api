from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://web-api.okjike.com/api/graphql"

@router.post("/api/graphql")
async def api_graphql(
    text: str,
    # host: Optional[str] = Header("web-api.okjike.com"),
    cookie: Optional[str] = Header("_ga=GA1.2.1329611284.1728629767; fetchRankedUpdate=1730736532039; _gid=GA1.2.1224935922.1730736532; _ga_LQ23DKJDEL=GS1.2.1730757159.7.1.1730758654.60.0.0; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoibGNSc0FtZHhGQWhod1M1RWdjcXduUGp5cDlGR0xGelhwbDlpdVVPdjdcL3k0RHhCd21YZ3hJSVJoQnRIRU9RQ0JnbXlcL0dvWis2WStuQ2FVZlk4eDZ2R3F2UTRxbElcL3RqckYrXC9DUFEwZFFacGJGM3Fsek1ySGM3R0QwSFE3bDE2aGQ5MUFvak9LZHMwdk01eU9XTU5GcTVNVmFWemxPY0JNbmhcL283V2F0ZXdsVUtkOEQzMU4zc0ZsaWRaTEk1UUxqZnR5WUV5ekxBY1lTSjBleGNRa3Npd3pvNHM1ek4wZ1J1OFpNbVhVQmluR2RVeDlsMHJjQWxaQmdQQVgzUlI0YnBHTjRueXdKK09TdWNjb2c3VGo1WEJCMllndHI4cmx4d2JYUWFrR0U3QjNHUU00UXdtdUJ2MGJcL0tURENpaG05Sll2dW1LMHY0N3FCbkJYcGhPUGtuRmk4OHpLc05yU0d4WGtVamgyU2dJPSIsInYiOjMsIml2IjoiVFBtMGVvcEtRTENsc2gwdVpRMWJQZz09IiwiaWF0IjoxNzMwNzU4OTcwLjI0M30.s5nR6klSxxeDRQEslr6XpUny76azfzCW9tx7tXlUIbc; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiR3l4aHM1Rm53aEdnTVlYVEFPRU5cL1VxS0Q5WFB2NWxLdlwvWkM1Qkt6clE2UzJMUWFTXC9veGdwNG5ZWlVsNE5JYVFLcXJYbTRocG16K1ZBekd0YkF5K3JqeTRaQlUzR0t2UUh6SjRLR09va2paSUR1VXYwYWpZQkJXMVlcL2hBUk94dlVIM25PVm1ybDNBbk9vZThmSVJjSlIxSFZWVjA4MlFqNnFHKzVGZE9hcz0iLCJ2IjozLCJpdiI6IktmNUlRZE5zYUVFbEhBUTh1bWR4emc9PSIsImlhdCI6MTczMDc1ODk3MC4yNDN9.Y2rwVQDHVoHxTg-bwD4qQ9S6puEuxaUR6CkJcMN3xqE"),
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
        # "Host": host,
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

        request_data: Dict[str, Any] = {
            'operationName': 'CreateMessage',
            'variables': {
                'message': {
                    'content': text,
                    'syncToPersonalUpdate': True,
                    'submitToTopic': '59747bef311d650011d5ab09',
                    'pictureKeys': []}},
            'query': 'mutation CreateMessage($message: CreateMessageInput!) { createMessage(input: $message) { success toast __typename } } '}

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

