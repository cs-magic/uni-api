import re
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse

# 指定接口返回的数据类型，一般是 dict，也有 list 或者 plain，或者 sse 的
RETURN_TYPES: Optional[str] = None


def convert_js_to_python_bool(json_str: str) -> str:
    """Convert JavaScript boolean values to Python boolean values"""
    return json_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')


def parse_curl_command(curl_command: str) -> Tuple[Dict, str, str, str, Optional[Dict]]:
    """Parse curl command and extract headers, method, url, path and data"""
    # Extract headers
    headers = {}
    header_pattern = r'-H\s*[\'"]([^\'"]+)[\'"]'
    header_matches = re.finditer(header_pattern, curl_command)
    for match in header_matches:
        header_line = match.group(1)
        if ':' in header_line:
            key, value = header_line.split(':', 1)
            key = key.strip()
            # Skip Host header as it will be automatically set by requests
            if key.lower() != "host":
                value = value.strip()
                # 处理特殊情况: \"\" -> ""
                value = re.sub(r'\\"+', '"', value)
                # 处理其他转义字符
                value = value.replace('\\\\', '\\')
                # 处理空字符串的特殊情况
                if value == '""':
                    value = ''
                headers[key] = value

    # Extract URL
    url_pattern = r'(?:"|\')?((https?://[^\s"\']+))(?:"|\')?(?:\s+--compressed|\s+)?(?:\s|$)'
    url_match = re.search(url_pattern, curl_command)
    url = url_match.group(1) if url_match else ""
    url = url.replace('\\"', '"').replace('\\\\', '\\')

    # Extract method
    method = "POST" if any(x in curl_command for x in ["--data-binary", "-d", "--data-raw"]) else "GET"

    # Extract request body data
    data = None
    # Add support for --data-raw
    data_patterns = [
        r'--data-binary\s*[\'"](\{.*?\})[\'"](?:\s+--compressed|\s|$)',
        r'--data-raw\s*\$?[\'"](\{.*?\})[\'"](?:\s+--compressed|\s|$)'
    ]
    
    for pattern in data_patterns:
        data_match = re.search(pattern, curl_command, re.DOTALL)
        if data_match:
            try:
                data_str = data_match.group(1).strip()
                data_str = data_str.replace('\\"', '"')
                data_str = data_str.replace('\\\\', '\\')
                data_str = data_str.replace('\\n', ' ')
                data_str = re.sub(r'\s+', ' ', data_str)
                # Convert JavaScript booleans to Python booleans
                data_str = convert_js_to_python_bool(data_str)
                data = eval(data_str)  # Using eval instead of json.loads to handle Python literals
                break
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
    code += f'@router.{method.lower()}("{path_name}")\n'
    code += f'async def {path_name.strip("/").replace("/", "_")}(\n'

    # Add parameters
    params = []

    # Add data parameter if it exists - keep it simple
    if data:
        params.append(f'    request_data: Dict[str, Any] = {data}')

    # Add header parameters
    for header, value in headers.items():
        header_var = header.lower().replace('-', '_')
        if value:
            value = value.replace('"', '\\"')
            value = f'"{value}"'
        else:
            value = '""'
        params.append(f'    {header_var}: Optional[str] = Header({value})')

    # Add parameters to function definition
    code += ',\n'.join(params)
    code += '\n)'
    if RETURN_TYPES:
        code += ' -> ' + RETURN_TYPES
    code += ":\n"

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

        # Send POST request with request_data directly
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=request_data,
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
    api = 'jike-search-quanzi'
    # api = 'jike-read-profile'

    with open(f'./.data/apis/{api}.sh') as f:
        res = generate_fastapi_route(f.read(), "/" + api.replace('-', '/'))
    with open(f'{api.replace("-", "_")}.py', 'w') as f:
        f.write(res)
    print(res)
