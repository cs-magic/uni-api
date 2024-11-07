import re
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse


def convert_js_to_python_bool(json_str: str) -> str:
    """Convert JavaScript boolean values to Python boolean values"""
    return json_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')


def parse_curl_command(curl_command: str) -> Tuple[Dict, str, str, str, Optional[Dict]]:
    """Parse curl command and extract headers, method, url, path and data"""
    # Extract headers
    headers = {}
    header_pattern = r'-H\s*"([^"]+)"'
    header_matches = re.finditer(header_pattern, curl_command)
    for match in header_matches:
        header_line = match.group(1)
        if ':' in header_line:
            key, value = header_line.split(':', 1)
            key = key.strip()
            # Skip Host header as it will be automatically set by requests
            if key.lower() != "host":
                headers[key] = value.strip()

    # Extract URL
    url_pattern = r'(?:"|\')?((https?://[^\s"\']+))(?:"|\')?(?:\s+)?$'
    url_match = re.search(url_pattern, curl_command)
    url = url_match.group(1) if url_match else ""

    # Extract method
    method = "POST" if " --data-binary " in curl_command or " -d " in curl_command else "GET"

    # Extract request body data
    data = None
    data_pattern = r'--data-binary\s*[\'"](\{.*?\})[\'"](?:\s+--compressed|\s|$)'
    data_match = re.search(data_pattern, curl_command, re.DOTALL)
    if data_match:
        try:
            data_str = data_match.group(1).strip()
            data_str = data_str.replace('\\"', '"').replace('\\n', ' ')
            data_str = re.sub(r'\s+', ' ', data_str)
            # Convert JavaScript booleans to Python booleans before parsing JSON
            data_str = convert_js_to_python_bool(data_str)
            data = eval(data_str)  # Using eval instead of json.loads to handle Python literals
        except Exception as e:
            print(f"Warning: Could not parse data: {e}")
            data = data_match.group(1)

    # Extract path from URL
    parsed_url = urlparse(url)
    path = parsed_url.path

    return headers, method, url, path, data


def generate_fastapi_route(curl_command: str, path_name: str) -> str:
    """Convert curl command to FastAPI route code"""
    headers, method, url, path, data = parse_curl_command(curl_command)

    # Generate imports
    code = '''from fastapi import APIRouter, Header
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

'''

    # Add URL constant
    code += f'BASE_URL = "{url}"\n\n'

    # Generate route function
    # Add route decorator
    code += f'@router.{method.lower()}("{path_name}")\n'

    # Start function definition
    code += f'async def {path_name.strip('/').replace('/', '_')}(\n'

    # Add parameters
    params = []

    # Add data parameter if it exists
    if data:
        # Convert the data dict to a string and handle boolean values
        data_str = str(data)
        params.append(f'    request_data: Dict[str, Any] = {data_str}')

    # Add header parameters
    for header, value in headers.items():
        header_var = header.lower().replace('-', '_')
        value = value.replace('"', '\\"')
        params.append(f'    {header_var}: Optional[str] = Header("{value}")')

    # Add parameters to function definition
    code += ',\n'.join(params)
    code += '\n) -> Dict[str, Any]:\n'

    # Add docstring
    code += f'    """\n    Route generated from curl command\n    Original URL: {url}\n    Method: {method}\n    """\n'

    # Add request implementation
    code += '''    # Construct headers
    headers = {'''

    # Add headers
    for header in headers:
        code += f'\n        "{header}": {header.lower().replace("-", "_")},'

    code += '''
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
'''

    # Add request code based on method
    if method.upper() == "POST":
        code += '''        # Send POST request
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=request_data,
            verify=True
        )
'''
    else:
        code += '''        # Send GET request
        response = requests.get(
            BASE_URL,
            headers=headers,
            verify=True
        )
'''

    # Add response handling
    code += '''        # Check response status
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
'''

    return code


# Example usage
if __name__ == "__main__":
    res = generate_fastapi_route(
        '''curl -H "Host: api.ruguoapp.com" -H "sec-ch-ua-platform: \"macOS\"" -H "x-jike-refresh-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiazVva1VQXC8zTTNpOUliQmpZOFFjdU5cL2xqMGpmMElETGhpOEJBZkl6ZFYxR3lWZ2RmWWxcL2llaHhQbDl3TGRPK0h3dVZkWUdqVm1oMFJMOWUwdVJxYkFBR3Z5YWRXYzFnZTE0dmFZNThhR0U1ZVE3Nk54a1NPT3F4R3VETmFVVXEzblRMN3hSRFhtbEVyN1dNOWVpY2hhWnptNmoybHg1UkxGSWV3d1czR20wPSIsInYiOjMsIml2Ijoia25ldTk4K01POTh6NzFEdDc4VlpEUT09IiwiaWF0IjoxNzMwOTAzMDA5LjE1Nn0.fs9VRliivfhHepsDX9rFtsGhwrPXedIfh53ebGPvDxU" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "sec-ch-ua-mobile: ?0" -H "app-version: 7.27.0" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: application/json, text/plain, */*" -H "x-jike-access-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiOWI2bTNNMFZ5TU9BZDFtaEFGeEVUOGxsZFlIYlwvZUk0Qk13d25QcU1nY2tHRTUyZ0h6T2xnREUrOE1VTmlVQUpkNWJ3ZkJpYmU3V0IrYlFhczlRMDJNVEtRSW51WGhXbjJHUGxwTm8reFRhbnUyTlpwVFRsVVFcL1piSzdZbjZFYU1aZGVRYk9EU1llMG5ibGZaK0JEZmp6Tk5YVG5RclVcL2toM01MUXZqQnp6XC9zeFpwUjZVa2xzbWphRGdTM0pneWRNXC9Gc2V2NDVvNGRPZHc0M2ptOXFmb2VJRUtUVHV4dERQRk81cU5ZR1JQZXdEbEZrYjZkbjZwXC9yVm1sNmZ6dmQ0V2ZHOCtMUHNnZXN4c29ocUdFQmdEa2s5S1JEQTJ6N3ZsSElaMU9QM21vU1VTNzdJazFVTVVYQmFnUno0WTM0enRjRmFaUGlvSmQ1R085VitpVW5jZUN5VzcwY3lYUG5oWTJJREpGRTdjPSIsInYiOjMsIml2IjoiMzBPY3FENVRaSGlvOUtqd3p0TlpiQT09IiwiaWF0IjoxNzMwOTAzMDA5LjE1Nn0.sKqVFu5iGDa-XhVn-5jDgrJ902cG1-LcRoFd-ztldhw" -H "dnt: 1" -H "origin: https://web.okjike.com" -H "sec-fetch-site: cross-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "referer: https://web.okjike.com/" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --compressed "https://api.ruguoapp.com/1.0/users/profile"''',
        '/jike/profile')

    res = generate_fastapi_route(
        '''curl -H "Host: api.zsxq.com" -H "Cookie: zsxq_access_token=A1A047AB-483F-F2F6-27EF-831393870534_1E07900F500D3426; zsxqsessionid=7ea23150bf6824166e923cd620adf32d; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2228242851215251%22%2C%22first_id%22%3A%22192f0c0191d1983-0199f37f9d1c95c-1f525636-3686400-192f0c0191e2a46%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZjBjMDE5MWQxOTgzLTAxOTlmMzdmOWQxYzk1Yy0xZjUyNTYzNi0zNjg2NDAwLTE5MmYwYzAxOTFlMmE0NiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjI4MjQyODUxMjE1MjUxIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2228242851215251%22%7D%7D; abtest_env=product" -H "sec-ch-ua-platform: \"macOS\"" -H "x-request-id: dff4f1bc8-eb5f-4724-a28c-0e775b7fde0" -H "x-version: 2.65.0" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "x-timestamp: 1730907137" -H "sec-ch-ua-mobile: ?0" -H "x-signature: 965d4028443950d8942100b5f66ec350d9be3383" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: application/json, text/plain, */*" -H "dnt: 1" -H "origin: https://wx.zsxq.com" -H "sec-fetch-site: same-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "referer: https://wx.zsxq.com/" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --compressed "https://api.zsxq.com/v3/users/self"''',
        '/zsxq/profile')

    res = generate_fastapi_route(
        '''curl -H "Host: web-api.okjike.com" -H "Cookie: _ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; fetchRankedUpdate=1730903010810; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiaVMycjV1Qm5BWFlHUkRoV3JuNzNFejZEaDdISjgrWHRQNGJHUEdwUG1GRmsrdUJ1b0hCWnpqelhqRXg2bjluRWJHaHhER0RHR1dNT3lGbXo0VFdCaFM0R1cxbDc5REc1MmNGbWRKWkhYN2xTOTdxWDIrMXZZUXh0dEZkUUxScWZiZHBuS0RSSlZFZFd3XC83dTdsa3kwekZ1NkxJQldVQlwvVzBEdlBkcjNFZDIrbzM2Vjk5Q0t3SGowbkJVaVlwXC8zcmlhb2Q3aHBXUytTaUxHZmNIcU1USjRSZGJcL3dTNGk3XC9VTjMrbkYzb0FjcnpvbHYxQVdkZEF6cnV5VmRYbGhpRFJiK3FCUDl4RFRwNE53MkMrcE5FWkU5RFlDZ3ZUZVBaNGRKRUlJYzFPZUF6UjNTdGpiSVhTV0VkblQwTThCQXJhTUUxN01nU0N0bmlxY2pBbkVDTGZ6VjNuU0N0WG9RT3FENmxYK3ZTemM9IiwidiI6MywiaXYiOiJHamU4S0pLZnhNTkVWd3g3dU9wV2V3PT0iLCJpYXQiOjE3MzA5MTA4NzAuMDJ9.u-Cz75T_zvLQE9cOF7O1YADbctoABvOd8GdFskG4HsA; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiaTNDSTJTMGF2S1wvVGszZkN5TWtLUXBtT2RRRGhGQzJKc2NqS0swUlUwV0dqYmVZbUZDODluYk9ZcXZydnFJWHpiMFVBVVBvbnRGZUl5MUNSdXFCMk92b29RQlI0dUZiVm9lY1dEdXZJOUhUR2RNZkV5S0RnU0ZQSlBXZmlNdXgyY2JyVENXR0VHd3k1a0p4UlArUTBWcUZCNmdLa0xYalVEMEVzeGlqZEF5MD0iLCJ2IjozLCJpdiI6InBlRnUxemU2RzZ4OCtieEZXMkY3ZVE9PSIsImlhdCI6MTczMDkxMDg3MC4wMn0.vphQL0uYVwhSPzom9NnCOiQyigXDsT7FRia1oxgGiQQ; _gat=1; _ga_LQ23DKJDEL=GS1.2.1730908772.14.1.1730911595.60.0.0" -H "sec-ch-ua-platform: \"macOS\"" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: */*" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "content-type: application/json" -H "dnt: 1" -H "sec-ch-ua-mobile: ?0" -H "origin: https://web.okjike.com" -H "sec-fetch-site: same-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --data-binary "{\"operationName\":\"SearchIntegrate\",\"variables\":{\"keywords\":\"创业者\"},\"query\":\"query SearchIntegrate($keywords: String!, $loadMoreKey: JSON) {\n  search {\n    integrate(keywords: $keywords, loadMoreKey: $loadMoreKey) {\n      pageInfo {\n        hasNextPage\n        loadMoreKey\n        __typename\n      }\n      highlightWord {\n        words\n        singleMaxHighlightTime\n        totalMaxHighlightTime\n        __typename\n      }\n      nodes {\n        ... on SearchIntegrateSection {\n          sectionType: type\n          sectionViewType\n          sectionContent: content\n          title\n          __typename\n        }\n        ... on SearchIntegrateUserSection {\n          items {\n            ...TinyUserFragment\n            following\n            __typename\n          }\n          __typename\n        }\n        ... on TopicInfo {\n          ...TopicItemFragment\n          __typename\n        }\n        ... on OriginalPost {\n          ...FeedMessageFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TinyUserFragment on UserInfo {\n  avatarImage {\n    thumbnailUrl\n    smallPicUrl\n    picUrl\n    __typename\n  }\n  isSponsor\n  username\n  screenName\n  briefIntro\n  __typename\n}\n\nfragment TopicItemFragment on TopicInfo {\n  id\n  messagePrefix\n  content\n  intro\n  subscribedStatusRawValue\n  subscribersCount\n  squarePicture {\n    smallPicUrl\n    middlePicUrl\n    picUrl\n    __typename\n  }\n  tips {\n    inComment\n    inDraft\n    __typename\n  }\n  subscribersTextSuffix\n  subscribersName\n  recentPost\n  __typename\n}\n\nfragment FeedMessageFragment on MessageEssential {\n  ...EssentialFragment\n  ... on OriginalPost {\n    ...LikeableFragment\n    ...CommentableFragment\n    ...RootMessageFragment\n    ...UserPostFragment\n    ...MessageInfoFragment\n    isPrivate\n    pinned {\n      personalUpdate\n      __typename\n    }\n    __typename\n  }\n  ... on Repost {\n    ...LikeableFragment\n    ...CommentableFragment\n    ...UserPostFragment\n    ...RepostFragment\n    isPrivate\n    pinned {\n      personalUpdate\n      __typename\n    }\n    __typename\n  }\n  ... on Question {\n    ...UserPostFragment\n    __typename\n  }\n  ... on OfficialMessage {\n    ...LikeableFragment\n    ...CommentableFragment\n    ...MessageInfoFragment\n    ...RootMessageFragment\n    __typename\n  }\n  __typename\n}\n\nfragment EssentialFragment on MessageEssential {\n  id\n  type\n  content\n  shareCount\n  repostCount\n  createdAt\n  collected\n  pictures {\n    format\n    watermarkPicUrl\n    picUrl\n    thumbnailUrl\n    smallPicUrl\n    width\n    height\n    __typename\n  }\n  urlsInText {\n    url\n    originalUrl\n    title\n    __typename\n  }\n  __typename\n}\n\nfragment LikeableFragment on LikeableMessage {\n  liked\n  likeCount\n  __typename\n}\n\nfragment CommentableFragment on CommentableMessage {\n  commentCount\n  __typename\n}\n\nfragment RootMessageFragment on RootMessage {\n  topic {\n    id\n    content\n    __typename\n  }\n  __typename\n}\n\nfragment UserPostFragment on MessageUserPost {\n  readTrackInfo\n  user {\n    ...TinyUserFragment\n    __typename\n  }\n  __typename\n}\n\nfragment MessageInfoFragment on MessageInfo {\n  video {\n    title\n    type\n    image {\n      picUrl\n      __typename\n    }\n    __typename\n  }\n  linkInfo {\n    originalLinkUrl\n    linkUrl\n    title\n    pictureUrl\n    linkIcon\n    audio {\n      title\n      type\n      image {\n        thumbnailUrl\n        picUrl\n        __typename\n      }\n      author\n      __typename\n    }\n    video {\n      title\n      type\n      image {\n        picUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment RepostFragment on Repost {\n  target {\n    ...RepostTargetFragment\n    __typename\n  }\n  targetType\n  __typename\n}\n\nfragment RepostTargetFragment on RepostTarget {\n  ... on OriginalPost {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    topic {\n      id\n      content\n      __typename\n    }\n    user {\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n  ... on Repost {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    user {\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n  ... on Question {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    user {\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n  ... on Answer {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    user {\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n  ... on OfficialMessage {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    __typename\n  }\n  ... on DeletedRepostTarget {\n    status\n    __typename\n  }\n  __typename\n}\n\"}" --compressed "https://web-api.okjike.com/api/graphql"''',
        '/jike/search')

    res = generate_fastapi_route(
        '''curl -H "Host: web-api.okjike.com" -H "Cookie: _ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; fetchRankedUpdate=1730903010810; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiSGlLallUa0YxVkczTlIrK2JvdlVSQnJrTlNhMWNYajhoR0VNd0FMRXM1OUh0dGtnXC9VS1AzQUhndmJFbFNWMTJzSmdZNmJTYmhGdzJjZGNBQkI0TitZV0lhV1JvVm9mR3l5eHFrNURJWWxMZXRuUlVoZDhLMmpKU09ZaGhvNFBEZ0JYaUxVWmp3OXg2aldyYmNcL1J5MW9HM0kzNXRvXC9uYU5TZjMxQlROMGFPVTF0Ukg3Y25ZR094b1hHRklYUTNNV1JESDdiVTlSbkVXRldcL1J0YlZ3dVMrVHpLNWxMNUltVjFMTCt2UVlrZnp0Yng3K09cL1VvclBBU2JsY0pKc2YwMFRwYXltalJ1dWdpOEpsSTI1SVBXVnp2RE9rUnFoSjdDS1gwaGxXaTRjS3Vsaklva1FxMnczam1Ldk5lOEFcL3BsT3Uza1NYQWswS0JaRUpVQnJtS1FKUVwvcXNFVUJ2RlJ0RnI0UVRCNVhOaz0iLCJ2IjozLCJpdiI6InRqSk9iTVRIK1wvKzZYdk1HVFBrU3pBPT0iLCJpYXQiOjE3MzA5NTg0NzMuMjU3fQ.plvg5UWPzr9BWIn8dKh8JeJ8bxXYwlaLWD8TAvLhaNQ; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoialBJelFNbjd1aGo2K1hDdVJHYVE5bzlYMVFCYWpcLzBqTnp4d2x4TnNVZHBGZWNsWStrV1ArejdnTnZRbVdTTHJyUXFFZWErbExzQ21EaFwvS2dyV2s3VHlmZUNQZjRCbTREOXprWGtXY0plU0wzWng2TnpJZTlyQlZWY2I2Z3RRa0k1bXplOEN5VWpzbVFuU1J3U3FEVjFiZWZcL1JuRlZNOGY3cVVzVFB1ZzlvPSIsInYiOjMsIml2IjoibEZSZlZsbUl0cVUrampaUk5mZjNCUT09IiwiaWF0IjoxNzMwOTU4NDczLjI1N30.IBcfVgRCPdtwa8AGIraFKHy89Ddu2s4Msq26jX50dTY; _gat=1; _ga_LQ23DKJDEL=GS1.2.1730958475.15.1.1730958580.49.0.0" -H "sec-ch-ua-platform: \"macOS\"" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: */*" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "content-type: application/json" -H "dnt: 1" -H "sec-ch-ua-mobile: ?0" -H "origin: https://web.okjike.com" -H "sec-fetch-site: same-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --data-binary "{\"operationName\":\"SearchIntegrate\",\"variables\":{\"keywords\":\"吐槽\"},\"query\":\"query SearchIntegrate($keywords: String!, $loadMoreKey: JSON) {\n  search {\n    integrate(keywords: $keywords, loadMoreKey: $loadMoreKey) {\n      pageInfo {\n        hasNextPage\n        loadMoreKey\n        __typename\n      }\n      highlightWord {\n        words\n        singleMaxHighlightTime\n        totalMaxHighlightTime\n        __typename\n      }\n      nodes {\n        ... on SearchIntegrateSection {\n          sectionType: type\n          sectionViewType\n          sectionContent: content\n          title\n          __typename\n        }\n        ... on SearchIntegrateUserSection {\n          items {\n            ...TinyUserFragment\n            following\n            __typename\n          }\n          __typename\n        }\n        ... on TopicInfo {\n          ...TopicItemFragment\n          __typename\n        }\n        ... on OriginalPost {\n          ...FeedMessageFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TinyUserFragment on UserInfo {\n  avatarImage {\n    thumbnailUrl\n    smallPicUrl\n    picUrl\n    __typename\n  }\n  isSponsor\n  username\n  screenName\n  briefIntro\n  __typename\n}\n\nfragment TopicItemFragment on TopicInfo {\n  id\n  messagePrefix\n  content\n  intro\n  subscribedStatusRawValue\n  subscribersCount\n  squarePicture {\n    smallPicUrl\n    middlePicUrl\n    picUrl\n    __typename\n  }\n  tips {\n    inComment\n    inDraft\n    __typename\n  }\n  subscribersTextSuffix\n  subscribersName\n  recentPost\n  __typename\n}\n\nfragment FeedMessageFragment on MessageEssential {\n  ...EssentialFragment\n  ... on OriginalPost {\n    ...LikeableFragment\n    ...CommentableFragment\n    ...RootMessageFragment\n    ...UserPostFragment\n    ...MessageInfoFragment\n    isPrivate\n    pinned {\n      personalUpdate\n      __typename\n    }\n    __typename\n  }\n  ... on Repost {\n    ...LikeableFragment\n    ...CommentableFragment\n    ...UserPostFragment\n    ...RepostFragment\n    isPrivate\n    pinned {\n      personalUpdate\n      __typename\n    }\n    __typename\n  }\n  ... on Question {\n    ...UserPostFragment\n    __typename\n  }\n  ... on OfficialMessage {\n    ...LikeableFragment\n    ...CommentableFragment\n    ...MessageInfoFragment\n    ...RootMessageFragment\n    __typename\n  }\n  __typename\n}\n\nfragment EssentialFragment on MessageEssential {\n  id\n  type\n  content\n  shareCount\n  repostCount\n  createdAt\n  collected\n  pictures {\n    format\n    watermarkPicUrl\n    picUrl\n    thumbnailUrl\n    smallPicUrl\n    width\n    height\n    __typename\n  }\n  urlsInText {\n    url\n    originalUrl\n    title\n    __typename\n  }\n  __typename\n}\n\nfragment LikeableFragment on LikeableMessage {\n  liked\n  likeCount\n  __typename\n}\n\nfragment CommentableFragment on CommentableMessage {\n  commentCount\n  __typename\n}\n\nfragment RootMessageFragment on RootMessage {\n  topic {\n    id\n    content\n    __typename\n  }\n  __typename\n}\n\nfragment UserPostFragment on MessageUserPost {\n  readTrackInfo\n  user {\n    ...TinyUserFragment\n    __typename\n  }\n  __typename\n}\n\nfragment MessageInfoFragment on MessageInfo {\n  video {\n    title\n    type\n    image {\n      picUrl\n      __typename\n    }\n    __typename\n  }\n  linkInfo {\n    originalLinkUrl\n    linkUrl\n    title\n    pictureUrl\n    linkIcon\n    audio {\n      title\n      type\n      image {\n        thumbnailUrl\n        picUrl\n        __typename\n      }\n      author\n      __typename\n    }\n    video {\n      title\n      type\n      image {\n        picUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment RepostFragment on Repost {\n  target {\n    ...RepostTargetFragment\n    __typename\n  }\n  targetType\n  __typename\n}\n\nfragment RepostTargetFragment on RepostTarget {\n  ... on OriginalPost {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    topic {\n      id\n      content\n      __typename\n    }\n    user {\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n  ... on Repost {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    user {\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n  ... on Question {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    user {\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n  ... on Answer {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    user {\n      ...TinyUserFragment\n      __typename\n    }\n    __typename\n  }\n  ... on OfficialMessage {\n    id\n    type\n    content\n    pictures {\n      thumbnailUrl\n      __typename\n    }\n    __typename\n  }\n  ... on DeletedRepostTarget {\n    status\n    __typename\n  }\n  __typename\n}\n\"}" --compressed "https://web-api.okjike.com/api/graphql"''',
        '/jike/search/quanzi')
    print(res)
