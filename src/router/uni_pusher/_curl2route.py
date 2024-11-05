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
    curl_command = '''curl -H "Host: web-api.okjike.com" -H "Cookie: _ga=GA1.2.1329611284.1728629767; _gid=GA1.2.1224935922.1730736532; fetchRankedUpdate=1730811992418; x-jike-access-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiWVBSc2FpUjZOZTc2NU9XK3hXdTV2dm5tZXBQendwR2lDazVpajRaZVlBSDJSa0FVN2llSmZcL1hZZWZ5dzNNb0lGMng5MXBmWUs0djFTcmZTZEJ4MGdmdVhRVk01MmRqNGQzZWpiQUFDZVkxOXVSZjdaRWRTM1A4YjBaMTBUc1ZxS2xDaXJlWk9jeUJcL0toaWVLY0VZY3NTcTBkWTdxT01nYjRyQXBIY0xCa2hSXC9NaU80bHdqY1UyYUo3alVjTWU5cjBxR28wQzk0d1QyRk8yalRId2NxOWNVNG9EU3pTRUYwQ2RMNU54RkVXTXRBQ0M2MHZzeXk3bDN1UTRvSkJcL0QzMStSQkhYb1VHeTBzcGRJTllEanp2dzVQc1U0eTNObWRLYjJPZVNMOW9ZdnRCRlM5ZEJpbWFvVCtrRDdlOHNXXC9FMCswQXBwTW8zUVgyZEVyOFI1TVdJTmd3Y09yS2RvVk1pcjBQZmxTaXc9IiwidiI6MywiaXYiOiJlSWU4dHlabERxS0IxU2dzdlFjc2V3PT0iLCJpYXQiOjE3MzA4MjAwNjMuNDcxfQ.a2SywrTLsOitMMZvs8Em49kV7AWQYGzTL2KSl7yva1g; x-jike-refresh-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiQ2lJOEI3djBwTkVqYXBBeHB5QXZ2S1wvVHVJdkpWYVBGb2FLb2dQZHlFNDFoU0YzWFYyVEloVkdwTHJNa3NWR05DRHY0MmlCNVVSNlwvZUlqcFFMM3VWUCt4dDlGZ1pYWGJUSWNPbDVFd1h3bTB0ektXTWgwMG5XcThuUWdMOFdITXBlUVFzdWtJSEtZdSthWURTQms1K2ErNXhLbHBtYUF0VE40UERKcDBpOXM9IiwidiI6MywiaXYiOiJKUDQ3R1g4YUVsN3h6SCtHZUc1NHNBPT0iLCJpYXQiOjE3MzA4MjAwNjMuNDcxfQ.3vK76b5a0LOjU4CUs7HyPMYQPH0nNjzDEdBbdkevQ-E; _gat=1; _ga_LQ23DKJDEL=GS1.2.1730818883.11.1.1730820133.60.0.0" -H "sec-ch-ua-platform: \"macOS\"" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: */*" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "content-type: application/json" -H "dnt: 1" -H "sec-ch-ua-mobile: ?0" -H "origin: https://web.okjike.com" -H "sec-fetch-site: same-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --data-binary "{\"operationName\":\"CreateMessage\",\"variables\":{\"message\":{\"content\":\"t023\",\"syncToPersonalUpdate\":true,\"pictureKeys\":[]}},\"query\":\"mutation CreateMessage($message: CreateMessageInput!) {\n  createMessage(input: $message) {\n    success\n    toast\n    __typename\n  }\n}\n\"}" --compressed "https://web-api.okjike.com/api/graphql"'''
    route_code = generate_fastapi_route(curl_command)
    print(route_code) 