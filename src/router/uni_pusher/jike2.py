from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

BASE_URL = "https://web-api.okjike.com/api/graphql"

@router.post("/jike")
async def api_graphql(
    text: str,
    # host: Optional[str] = Header("web-api.okjike.com"),
    cookie: Optional[str] = Header("_ga=GA1.2.1329611284.1728629767; fetchRankedUpdate=1730736532039; _gid=GA1.2.1224935922.1730736532; _ga_LQ23DKJDEL=GS1.2.1730757159.7.1.1730759236.60.0.0; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoidmk5cjhwR0QwSXBuY290aHNyMUxNclQ4dmR2TzZ2VU1FQVArNlwvKzg1UVpQXC90Vk9sdVwvTjVpcUN2MU0zaTBwMlhiNmdGZmY1RnlHUnRERFRhRmNVbTE4MFo1YVA2K1oxekNSd29TU1ByVnR5cklQWll6dGtsVGF0c0RTQjdLNlBiVEk4RFNNZk9TMk1LN1wvN2VQeFFpODlueE9NUG12YVFEeFNBaG9TYlladGJDM2VCajJXXC9MdGhZOWpNTnUxXC8xUFNuZzRuNWYzeWRIRUpLT2dFRjJDOGJ5N1wvQVhza2QzSVwvbEM3SmUxTVdrdGQ1a2pxeDhGanNKRWRabE1YM0wwTk85Ymc0NmVaSk9BU2ZCWWcyMmpKM2VBTGo5K1poclRROEN5akdzODJhYjB3dkJUSEVYS1ltTmlaVWhvVlZGYklyZ21PQ3RlV1o0a1NNelwvTVBqNlowZ2hcL3dTZzkydEFwNTFaaE15SWhjUT0iLCJ2IjozLCJpdiI6IkVScnVBcFc0cHIzN2s5Q2hmZjFhWlE9PSIsImlhdCI6MTczMDc3NzgwOS41Mjh9.YpDpmhKWgyR4Q50BH0sYr0XxPjf5p6wKiVCbISLLgsQ; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoidjFjQnE0alwvaFVlSXdMVnBINW81QnRnemlmRUxIN0tWaXFucmdMODJ5VE9hTDVQZzNMRDVEM0dRWVRqQ25Dc2ZQZk90UVAwUVgrckFQQ2pscG81RzJqYVNcL3BJd3NySW8rWFZZUlVxeW44cnRHRlRKdWNRSzY2N2RjYVlJUW80Rjc3TXQ5OFY3eDBnM1ZFOHlKZkxhb0NreUJweDY3XC9OQTJINm4yVjZBQVB3PSIsInYiOjMsIml2IjoiUXo2TFFTc211MFdcLytUQVVCOXdjRWc9PSIsImlhdCI6MTczMDc3NzgwOS41Mjh9.rI0tzhvznvdJsNBosNHub8thJgRFJFqgCKj1tkNEQQQ"),
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

