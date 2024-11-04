import fastapi
from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter(prefix='/jike')

BASE_URL = "https://web-api.okjike.com/api/graphql"


@router.post("/push")
async def api_graphql(
    text: str,
    cookie: Optional[str] = Header(
        "_ga=GA1.2.1329611284.1728629767; fetchRankedUpdate=1730736532039; _gid=GA1.2.1224935922.1730736532; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiMWNwb3pQQ0dTODkyTFdIa2VxVVwvdEV1Y0pYS0dGSDFlRGlteVJLdmpNZmpKb3JoRE1NeFNaRm9aQU5aeFZLMHA4SzV3YmJJcWFsUVJNWENzWkxJNWNkNWFha0hZNHNzUkM4dXluRHJzblFibCtqdmltMFVjVGNLNHNqWUJ6Mk1FYnlPdlkxa3FXR0VhOGgxb21tQTVsdTNYRkg2XC9BdGN4N082a1IyQms2Q0ZMclNkU00yRWgzOVZzYThOZ1c0QlFYVm5WM3I1OXR5RDdhZXBsREdCclNyTnlwV1A4YUNRRFVhVWFiMG00VzRjSEVndXBRZDFVSUlIR0hGUk1VSmdCdEU4RzB6OUFKVzNjbTZcLzdIbkl0MmNkZzBCN01FNVwvY3BJY3pqemtYaDBTOEVUMXFHcndxYkxDaUFrM1F3Q0I3dkxwYjhZSlJEcWlPcVwvOEZuVUN0ZFpPZE9BcGdGNGZ3Zm1VNEJVZDdpYm89IiwidiI6MywiaXYiOiJ5SExPZTB4eURBZEhZWitzNlwvVm94UT09IiwiaWF0IjoxNzMwNzU3MTU3LjQ4NH0.171Q4BnTTh_1a80sImyAiI_04V1HEWNUtfPtY3c_i0o; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiTWd3THpyOGNpbVFLTGNHTkhJalIrd0FFdmhaNUJHTkgrRXJiZ2grYjR0WEhIb3R1UzVBa0tnU3dKM0Z5VFRFM2FnQ1owdmZ2QXl1XC9cLzhLbmx2WWZIVXVCbDhSMU1IVFhJYjIzRVlGUStYM0VlN0hzZTIwQk1MWkdqZnVuYmx1VVpYXC9cL1NmXC9SS3dyRE1HNWVJOUhYNTNuU1pUamRTK1FvTDZRNmlyVTh0cG89IiwidiI6MywiaXYiOiJYZXVoTHhyMUVqYlBwRjBrUk5teEZnPT0iLCJpYXQiOjE3MzA3NTcxNTcuNDg0fQ.dow6NCdvw6dDSiFDOEFmKQBwI6KUXKQF07ET5wis3JA; _ga_LQ23DKJDEL=GS1.2.1730757159.7.1.1730757197.22.0.0"),

    sec_ch_ua_platform: Optional[str] = Header(""),
    user_agent: Optional[str] = Header(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
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
) -> Dict[str, Any] | list:
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
        request_data = {
            'operationName': 'CreateMessage',
            'variables': {
                'message': {
                    'content': text,
                    'syncToPersonalUpdate': True,
                    'submitToTopic': '59747bef311d650011d5ab09',
                    'pictureKeys': []}},
            'query': 'mutation CreateMessage($message: CreateMessageInput!) { createMessage(input: $message) { success toast __typename } } '},
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
        except (json.JSONDecodeError):
            return {"response": response.text}

    except (requests.exceptions.RequestException,) as e:
        return {
            "error": str(e),
            "status_code": getattr(e.response, "status_code", None),
            "response_text": getattr(e.response, "text", None)
        }
