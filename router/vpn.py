import io
import os
import zipfile
from enum import Enum
from pathlib import Path

import cachetools
import requests
from fastapi import APIRouter, HTTPException, Request
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
CLASH_DATA_DIR.mkdir(exist_ok=True)
CLASH_CONFIG_DIR = CLASH_DATA_DIR / "config"
CLASH_CONFIG_DIR.mkdir(exist_ok=True)
CLASH_EXEC_DIR = CLASH_DATA_DIR / "exec"
CLASH_EXEC_DIR.mkdir(exist_ok=True)
CONFIG_FILEPATH = CLASH_CONFIG_DIR / CONFIG_FILENAME


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


@vpn_router.get('/clash.zip')
async def install_vpn(
    clash_version='2.0.24', clash_platform="linux_amd64", ):
    clash_exec_name = f'clash_{clash_version}_{clash_platform}.tar.gz'
    clash_exec_path = CLASH_EXEC_DIR / clash_exec_name
    if not clash_exec_path.exists():
        logger.info(f"pulling {clash_exec_name}")
        with open(clash_exec_path, 'wb') as f:
            res = requests.get(f'https://github.com/doreamon-design/clash/releases/download/v{clash_version}/{clash_exec_name}')
            f.write(res.content)
    # todo: 如果没有正常写入，则应该删除文件

    if not CONFIG_FILEPATH.exists():
        logger.info("pulling config file")
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

    return StreamingResponse(zip_buffer,
                             media_type='application/zip',
                             headers={'Content-Disposition': f'attachment; filename="clash.zip"'})


@vpn_router.get('/install-clash.sh')
@standard_error_handler()
async def get_install_clash():
    """返回安装脚本文件"""
    if not (DATA_PATH / "install-clash.sh").exists():
        raise HTTPException(status_code=404, detail="Install script not found")
    return FileResponse(DATA_PATH / "install-clash.sh", media_type="text/x-sh", filename="install-clash.sh")
