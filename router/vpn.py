import io
import os
import time
import zipfile
from enum import Enum
from functools import lru_cache
from pathlib import Path

import cachetools
from fastapi import APIRouter, Request
from fastapi.params import Depends
from starlette.responses import StreamingResponse, FileResponse

from packages.api.index import api
from packages.fastapi.standard_error import standard_error_handler
from utils.log import logger
from utils.path import DATA_PATH

vpn_router = APIRouter(prefix='/vpn', tags=["VPN"])


class Provider(str, Enum):
    foosber = "foosber"
    biznet = "biznet"

CONFIG_FILENAME = "config.yaml"
CLASH_DATA_DIR = DATA_PATH / "clash"
CONFIG_DIR = CLASH_DATA_DIR / "config"
CONFIG_FILEPATH = CONFIG_DIR / CONFIG_FILENAME

# 确保必要的目录存在
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


@cachetools.func.ttl_cache(ttl=60 * 10, maxsize=None)
def fetch_latest_config(
    provider: Provider = "foosber"
):
    logger.info("fetching latest config")

    if provider == "foosber":
        content_raw = api.get('https://xn--eckvarq8ld5k.xn--zckq7gxe.xn--tckwe/link/4lHIflFQQsH1S8qM?clash=1').text

        # modify linkedin.com
        domain = 'linkedin.com'
        router_from = 'DIRECT'
        router_to = '🔰 国外流量'
        content = content_raw.replace(f'{domain},{router_from}', f'{domain},{router_to}')

        # add chatgpt.com
        if "chatgpt.com" not in content:
            lines = content.splitlines()
            for index, line in enumerate(lines):
                if "openai.com" in line:
                    lines.insert(index, line.replace("openai.com", "chatgpt.com"))
                    content = "\n".join(lines)
                    break

    elif provider == "biznet":
        target_url = "https://let.bnsubservdom.com/api/v1/client/subscribe?token=d0a451156361a39cfd8219490f1f65ce"
        content = api.get(target_url, headers={"User-Agent": "clash-verge/v2.0.0"}).text

    else:
        raise Exception("not supported provider")
    with open(CONFIG_FILEPATH, 'w') as f:
        f.write(content)
    return content


@vpn_router.get('/config')
@standard_error_handler()
async def get_vpn_config(  # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    request: Request, content=Depends(fetch_latest_config)
):
    headers = {'Content-Disposition': f'attachment; filename="{CONFIG_FILENAME}"'}
    return StreamingResponse(io.BytesIO(content.encode('utf-8')), media_type='text/plain', headers=headers)


@vpn_router.get('/install')
async def install_vpn(update_cache=True, machine='ubuntu', time=time.time()):
    if not CONFIG_FILEPATH.exists():
        fetch_latest_config()
    
    # 在内存中创建 zip 文件
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(CLASH_DATA_DIR):
            for file in files:
                if file.endswith('.zip'):  # Skip other zip files
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(CLASH_DATA_DIR)
                zipf.write(file_path, arcname)
    
    # 将指针移到开始位置
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type='application/zip',
        headers={'Content-Disposition': f'attachment; filename="clash.zip"'}
    )
