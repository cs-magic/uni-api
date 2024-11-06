import re
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse
import json
import sys

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
        '/jike/profile'
    )

    res = generate_fastapi_route(
        '''curl -H "Host: api.zsxq.com" -H "Cookie: zsxq_access_token=A1A047AB-483F-F2F6-27EF-831393870534_1E07900F500D3426; zsxqsessionid=7ea23150bf6824166e923cd620adf32d; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2228242851215251%22%2C%22first_id%22%3A%22192f0c0191d1983-0199f37f9d1c95c-1f525636-3686400-192f0c0191e2a46%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZjBjMDE5MWQxOTgzLTAxOTlmMzdmOWQxYzk1Yy0xZjUyNTYzNi0zNjg2NDAwLTE5MmYwYzAxOTFlMmE0NiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjI4MjQyODUxMjE1MjUxIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2228242851215251%22%7D%7D; abtest_env=product" -H "sec-ch-ua-platform: \"macOS\"" -H "x-request-id: dff4f1bc8-eb5f-4724-a28c-0e775b7fde0" -H "x-version: 2.65.0" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "x-timestamp: 1730907137" -H "sec-ch-ua-mobile: ?0" -H "x-signature: 965d4028443950d8942100b5f66ec350d9be3383" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: application/json, text/plain, */*" -H "dnt: 1" -H "origin: https://wx.zsxq.com" -H "sec-fetch-site: same-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "referer: https://wx.zsxq.com/" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --compressed "https://api.zsxq.com/v3/users/self"''',
        '/zsxq/profile'
    )

    print(res)