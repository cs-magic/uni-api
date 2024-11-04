import re
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse
import json

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
    method = "POST" if "--data-binary" in curl_command or "-d" in curl_command else "GET"
    
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

def generate_fastapi_route(curl_command: str) -> str:
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
    function_name = path.replace('/', '_').strip('_') or 'root'
    if function_name.startswith('v2_'):
        function_name = function_name[3:]
    
    # Add route decorator
    code += f'@router.{method.lower()}("{path}")\n'
    
    # Start function definition
    code += f'async def {function_name}(\n'
    
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
    curl_command = '''curl -H "Host: web-api.okjike.com" -H "Cookie: _ga=GA1.2.1329611284.1728629767; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiWXloUlwvUXhQSXNIV1MrMzB0VjJjRHhzK3V4M2lMbUlhckhrdzNpdVwvRGpITUdCVXh3T3pjQ1hGaGlJNGlmTW9wdUZWNXo4disyVVdNNkt6TUNhUUg5UDJWUlh2T1M4U3RFSnlMcnlyTTNXeEliYVZrQWxzemxuQlRjeW9keUZJWFJpViszVXNFbkw3TUtFZHJsWnJkUTNQZjkzdTlDYVwvYnU1Y2xEZUFBbDIrNE9ZWXh5UWtEY1M2RllNOHhxM28wbUNrWGQzQ0tnc3ZzR0x3ajZlcXhcL3BkaVlKMURYNmhuTEJpeXo1eTVGWHpmTXhtVDQ5TjJoWjVjbit3RnZBSHJYSjc5QTh1TnJaa2diWWlBVGJQa1NhUHJRcmFUZXlwVzlCbnVPaEV0VVRuNVYxN3pRaVpvamF2aUEwU2NoRUdyQ0ZTTVdIWjB4SVArcHZ3Um5EbmVyeTdleE5WdnZ6UFVYUUtydUJcL2J6dU09IiwidiI6MywiaXYiOiJxczVmcHk3a0MyaE5EaFFkWk1qVTNBPT0iLCJpYXQiOjE3MzA3MzY1MjkuNTU3fQ.tmuTQ1E4WXdH6A8xJFJrngcSs2jKSuvIwZLuFnstPCA; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoib2toV1VTXC9kYkQ0ZzI1MXl3NU1VQjBcL3h3Y0VzRXdBZXREMEhFOTFWYXJhMW5QNGJMaXpUMVZxZmNqbk0rNm1pVjA4dldKMFIwYVJmNzVTeEVwRFR1eVgzdXV0SVwvQVRiWG03QVFvVVwveTlDalwvZlppYTd5aUJuU2poZGlLZmpWQ2dHVDdcL2VINjRLYmtOcWpGbTlyUE1OeWlHdHM4QkFKaW1sRElIV0xiQ1VVPSIsInYiOjMsIml2IjoiSFc3WW5wbmdGS2hWZDY2TmVQV1ZrUT09IiwiaWF0IjoxNzMwNzM2NTI5LjU1N30.O5yL2NdEG4ucKJc2_cVk98F3SVHH8xXiXoVitCTcZjo; fetchRankedUpdate=1730736532039; _gid=GA1.2.1224935922.1730736532; _ga_LQ23DKJDEL=GS1.2.1730736532.5.0.1730736532.60.0.0" -H "sec-ch-ua-platform: \"macOS\"" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: */*" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "content-type: application/json" -H "dnt: 1" -H "sec-ch-ua-mobile: ?0" -H "origin: https://web.okjike.com" -H "sec-fetch-site: same-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --data-binary "{\"operationName\":\"CreateMessage\",\"variables\":{\"message\":{\"content\":\"tttest1\",\"syncToPersonalUpdate\":true,\"submitToTopic\":\"59747bef311d650011d5ab09\",\"pictureKeys\":[]}},\"query\":\"mutation CreateMessage($message: CreateMessageInput!) {\n  createMessage(input: $message) {\n    success\n    toast\n    __typename\n  }\n}\n\"}" --compressed "https://web-api.okjike.com/api/graphql"'''
#     '''curl -H "Host: api.zsxq.com" -H "Cookie: zsxq_access_token=A1A047AB-483F-F2F6-27EF-831393870534_1E07900F500D3426; zsxqsessionid=7ea23150bf6824166e923cd620adf32d; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2228242851215251%22%2C%22first_id%22%3A%22192f0c0191d1983-0199f37f9d1c95c-1f525636-3686400-192f0c0191e2a46%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZjBjMDE5MWQxOTgzLTAxOTlmMzdmOWQxYzk1Yy0xZjUyNTYzNi0zNjg2NDAwLTE5MmYwYzAxOTFlMmE0NiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjI4MjQyODUxMjE1MjUxIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2228242851215251%22%7D%7D; abtest_env=product" -H "x-request-id: 239dc4d1c-0679-f2cc-d21c-d3dcd822013" -H "x-version: 2.64.0" -H "sec-ch-ua-platform: \"macOS\"" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "x-timestamp: 1730731549" -H "sec-ch-ua-mobile: ?0" -H "x-signature: 90500d7ba435ab968bf0193996b27ff68e4850c2" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: application/json, text/plain, */*" -H "dnt: 1" -H "content-type: application/json" -H "origin: https://wx.zsxq.com" -H "sec-fetch-site: same-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "referer: https://wx.zsxq.com/" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --data-binary "{
# 	\"req_data\": {
# 		\"mentioned_user_ids\": [],
# 		\"file_ids\": [],
# 		\"image_ids\": [],
# 		\"text\": \"tttest2\n\",
# 		\"type\": \"topic\"
# 	}
# }" --compressed "https://api.zsxq.com/v2/groups/51111828288514/topics"'''
    route_code = generate_fastapi_route(curl_command)
    print(route_code) 