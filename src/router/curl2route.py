import re
from typing import Dict, Tuple
from urllib.parse import urlparse
import json
import subprocess
import shlex
import gzip
import io

def parse_curl_command(curl_command: str) -> Tuple[Dict, str, str, str, Dict]:
    """Parse curl command and extract headers, method, url, and data"""
    # 提取headers
    headers = {}
    header_pattern = r'-H\s*"([^"]+)"'
    header_matches = re.finditer(header_pattern, curl_command)
    for match in header_matches:
        header_line = match.group(1)
        if ':' in header_line:
            key, value = header_line.split(':', 1)
            headers[key.strip()] = value.strip()
    
    # 提取URL - 修改为查找最后的URL模式
    url_pattern = r'(?:"|\')?((https?://[^\s"\']+))(?:"|\')?(?:\s+)?$'
    url_match = re.search(url_pattern, curl_command)
    url = url_match.group(1) if url_match else ""
    
    # 提取请求方法 (默认为GET)
    method = "POST" if "--data-binary" in curl_command or "-d" in curl_command else "GET"
    
    # 提取请求体数据 - 改进数据提取模式
    data = None
    data_pattern = r'--data-binary\s*[\'"](\{.*?\})[\'"](?:\s+--compressed|\s|$)'
    data_match = re.search(data_pattern, curl_command, re.DOTALL)
    if data_match:
        try:
            data_str = data_match.group(1).strip()
            # Handle escaped characters and normalize newlines
            data_str = data_str.replace('\\"', '"')
            data_str = re.sub(r'\\n\s*', ' ', data_str)  # Replace \n with space
            data_str = re.sub(r'\s+', ' ', data_str)  # Normalize whitespace
            data = json.loads(data_str)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON data: {e}")
            data = data_match.group(1)
    
    # 从URL中提取路径
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    return headers, method, url, path, data

def curl_to_fastapi_route(curl_command: str) -> str:
    """Convert curl command to FastAPI route code"""
    headers, method, url, path, data = parse_curl_command(curl_command)
    
    if not url:
        raise ValueError("No URL found in curl command")
    
    # 生成路由代码
    code = f'''from fastapi import APIRouter, Header, Response
from typing import Optional, Dict, Any
import requests
import json

router = APIRouter()

# 原始请求URL
ORIGINAL_URL = "{url}"

'''
    
    # 生成路由函数
    function_name = path.replace('/', '_').strip('_') or 'root'
    if function_name.startswith('v2_'):
        function_name = function_name[3:]
        
    code += f'''@router.{method.lower()}("{path}")'''
    
    # 添加函数定义
    code += f'''
async def {function_name}('''
    
    # 添加参数
    params = []
    if data:
        params.append(f'request_data: Dict[str, Any] = {json.dumps(data)}')
    
    # 添加header参数，带默认值
    for header, value in headers.items():
        header_var = header.lower().replace('-', '_')
        # 处理字符串中的引号，确保生成的代码语法正确
        value = value.replace('"', '\\"')
        params.append(f'{header_var}: Optional[str] = Header("{value}")')
    
    code += ', '.join(params)
    code += ''') -> Dict[str, Any]:
    """
    Proxy route automatically generated from curl command
    Original URL: {url}
    Method: {method}
    """
    # 构建请求头
    headers = {'''
    
    # 添加原始headers
    for header in headers:
        code += f'''
        "{header}": {header.lower().replace('-', '_')},'''
    
    code += '''
    }
    
    # 移除None值的headers
    headers = {k: v for k, v in headers.items() if v is not None}
    
    try:'''
    
    # 在发送请求之前添加一些额外的头信息
    code += '''
        # 添加一些额外的头信息
        if "Accept-Encoding" not in headers:
            headers["Accept-Encoding"] = "gzip, deflate, br"
        if "Connection" not in headers:
            headers["Connection"] = "keep-alive"
        if "Pragma" not in headers:
            headers["Pragma"] = "no-cache"
        if "Cache-Control" not in headers:
            headers["Cache-Control"] = "no-cache"
            
        print(f"Sending request to: {ORIGINAL_URL}")
        print(f"Headers: {headers}")'''
    
    if method.upper() == "POST":
        code += '''
        if request_data:
            print(f"Request data: {request_data}")
            
        import subprocess
        import shlex
        import gzip
        import io
        
        # 构建curl命令
        curl_command = f"""curl -H "Host: api.zsxq.com" """
        for header, value in headers.items():
            # 处理特殊字符
            value = value.replace('"', '\\"')
            curl_command += f'-H "{header}: {value}" '
        
        # 正确处理 JSON 数据
        if request_data:
            # 确保 JSON 数据被正确转义
            json_str = json.dumps(request_data)
            # 转义双引号和其他特殊字符
            json_str = json_str.replace('"', '\\"').replace('$', '\\$')
            curl_command += f'--data-binary "{json_str}" '
            
        curl_command += '--compressed '
        curl_command += f'"{ORIGINAL_URL}"'
        
        print(f"Executing curl command: {curl_command}")
        
        # 执行curl命令
        try:
            # 使用 list 形式传递参数，避免 shell 解析问题
            curl_args = ['curl', '-H', 'Host: api.zsxq.com']
            
            # 添加 headers
            for header, value in headers.items():
                curl_args.extend(['-H', f'{header}: {value}'])
            
            # 添加数据
            if request_data:
                curl_args.extend(['--data-binary', json.dumps(request_data)])
            
            # 添加其他参数
            curl_args.extend(['--compressed', ORIGINAL_URL])
            
            print(f"Executing curl with args: {curl_args}")
            
            result = subprocess.run(
                curl_args,
                capture_output=True,
                check=True
            )'''
    else:
        code += '''
        # 发送GET请求
        session = requests.Session()
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
        
        response = session.get(
            ORIGINAL_URL,
            headers=headers,
            verify=True,
            allow_redirects=True
        )
        
        # 检查响应状态码
        response.raise_for_status()
        
        # 尝试解析JSON响应
        try:
            return response.json()
        except json.JSONDecodeError:
            # 如果响应不是JSON格式，返回原始文本
            return {"response": response.text}'''
    
    code += '''
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": getattr(e.response, 'status_code', None),
            "response_text": getattr(e.response, 'text', None)
        }
    except Exception as e:
        return {"error": str(e)}
'''
    
    return code

# 示例使用
if __name__ == "__main__":
    # 测试用的curl命令
    curl_command = '''curl -H "Host: api.zsxq.com" -H "Cookie: zsxq_access_token=A1A047AB-483F-F2F6-27EF-831393870534_1E07900F500D3426; zsxqsessionid=7ea23150bf6824166e923cd620adf32d; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2228242851215251%22%2C%22first_id%22%3A%22192f0c0191d1983-0199f37f9d1c95c-1f525636-3686400-192f0c0191e2a46%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZjBjMDE5MWQxOTgzLTAxOTlmMzdmOWQxYzk1Yy0xZjUyNTYzNi0zNjg2NDAwLTE5MmYwYzAxOTFlMmE0NiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjI4MjQyODUxMjE1MjUxIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2228242851215251%22%7D%7D; abtest_env=product" -H "x-request-id: 239dc4d1c-0679-f2cc-d21c-d3dcd822013" -H "x-version: 2.64.0" -H "sec-ch-ua-platform: \"macOS\"" -H "sec-ch-ua: \"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"" -H "x-timestamp: 1730731549" -H "sec-ch-ua-mobile: ?0" -H "x-signature: 90500d7ba435ab968bf0193996b27ff68e4850c2" -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" -H "accept: application/json, text/plain, */*" -H "dnt: 1" -H "content-type: application/json" -H "origin: https://wx.zsxq.com" -H "sec-fetch-site: same-site" -H "sec-fetch-mode: cors" -H "sec-fetch-dest: empty" -H "referer: https://wx.zsxq.com/" -H "accept-language: en-US,en;q=0.9" -H "priority: u=1, i" --data-binary "{
	\"req_data\": {
		\"mentioned_user_ids\": [],
		\"file_ids\": [],
		\"image_ids\": [],
		\"text\": \"tttest2\n\",
		\"type\": \"topic\"
	}
}" --compressed "https://api.zsxq.com/v2/groups/51111828288514/topics"'''
    route_code = curl_to_fastapi_route(curl_command)
    print(route_code)
