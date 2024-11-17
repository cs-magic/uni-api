import re
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse
from jinja2 import Environment, PackageLoader, select_autoescape
from sqlalchemy.testing.plugin.plugin_base import logging

# 指定接口返回的数据类型，一般是 dict，也有 list 或者 plain，或者 sse 的
RETURN_TYPES: Optional[str] = None

# 创建 Jinja2 环境
env = Environment(
    loader=PackageLoader('src.router.uni_pusher', '../templates'),
    trim_blocks=False,
    lstrip_blocks=True,
    keep_trailing_newline=False,
)


def convert_js_to_python_bool(json_str: str) -> str:
    """Convert JavaScript boolean values to Python boolean values"""
    return json_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')


def parse_form_data(data_raw: str) -> Dict:
    """Parse form-data from curl command"""
    form_data = {}
    # Split by boundary
    parts = data_raw.split('------WebKitFormBoundary')
    
    for part in parts:
        if not part.strip():
            continue
            
        # Extract name, filename, and content-type
        name_match = re.search(r'name="([^"]+)"', part)
        if name_match:
            name = name_match.group(1)
            
            # Check if this is a file upload
            filename_match = re.search(r'filename="([^"]+)"', part)
            content_type_match = re.search(r'Content-Type:\s*([^\r\n]+)', part)
            
            if filename_match:
                filename = filename_match.group(1)
                content_type = content_type_match.group(1) if content_type_match else None
                form_data[name] = {
                    'type': 'file',
                    'filename': filename,
                    'content_type': content_type
                }
            else:
                # Extract value for non-file fields
                content_parts = part.split('\r\n\r\n')
                if len(content_parts) > 1:
                    # Get everything after the headers until the next boundary or end
                    value = content_parts[1].strip()
                    if value.endswith('--'):
                        value = value[:-2]
                    form_data[name] = {
                        'type': 'field',
                        'value': value
                    }
    
    return form_data


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
    method = "POST" if any(x in curl_command for x in ["--data-binary", " -d ", "--data-raw"]) else "GET"

    # Extract request body data
    data = None
    is_multipart = False
    
    # Check if it's multipart/form-data
    if 'multipart/form-data' in curl_command:
        is_multipart = True
        # 修改正则表达式以更准确地匹配 multipart form-data
        data_pattern = r'--data-raw\s*\$?[\'"]([\s\S]+?)[\'"](?:\s+--compressed|\s|$)'
        data_match = re.search(data_pattern, curl_command)
        
        if data_match:
            # 获取原始数据并处理转义字符
            raw_data = data_match.group(1)
            raw_data = raw_data.replace('\\r\\n', '\r\n')  # 处理换行符
            raw_data = raw_data.replace('\\', '')  # 处理其他转义字符
            data = parse_form_data(raw_data)
            print("Parsed form data:", data)  # 调试输出
    else:
        # Original data extraction for JSON payloads
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
                    data_str = convert_js_to_python_bool(data_str)
                    data = eval(data_str)
                    break
                except Exception as e:
                    print(f"Warning: Could not parse data: {e}")
                    data = data_match.group(1)

    # Extract path from URL
    parsed_url = urlparse(url)
    path = parsed_url.path

    return headers, method, url, path, data


def generate_fastapi_route(curl_command: str, path_name: str, route_variable_name: str) -> str:
    """Convert curl command to FastAPI route code using Jinja2 template"""
    headers, method, url, path, data = parse_curl_command(curl_command)
    
    # Check if this is a file upload route
    is_file_upload = data and any(field.get('type') == 'file' for field in data.values())

    # 获取模板
    template = env.get_template('fastapi_route.py.j2')
    
    # 准备模板变量
    template_vars = {
        'route_variable_name': route_variable_name,
        'path_name': path_name,
        'method': method,
        'url': url,
        'headers': headers,
        'data': data,
        'is_file_upload': is_file_upload,
        'return_types': RETURN_TYPES,
        'route_function_name': re.sub(r"[-/.]", "_", path_name.strip("/")),
    }

    print(data)
    
    # 渲染模板
    rendered = template.render(**template_vars)
    return rendered


# Example usage
if __name__ == "__main__":
    api = ('jike_upload-image.sh'
           .replace('.sh', ''))
    route_path = '/' + api.replace('_', '/')
    route_variable_name = api.replace('-', '_') + "_route"

    with open(f'./.data/apis/{api}.sh') as f:
        res = generate_fastapi_route(f.read(), route_path, route_variable_name)
    with open(f'{api.replace("-", "_")}.py', 'w') as f:
        f.write(res)
    print(res)

