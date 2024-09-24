import io
import time

import httpx
from fastapi import APIRouter, Request, HTTPException
from starlette.responses import StreamingResponse, Response

from packages.common_api.index import api
from packages.common_fastapi.error_handler import error_handler

vpn_router = APIRouter(prefix='/vpn', tags=["VPN"])


async def fetch_with_session(url, headers):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 首先尝试访问主页以获取任何必要的 cookie
        await client.get("https://dist.bnsubservdom.com/")

        # 然后进行实际的请求
        response = await client.get(url, headers=headers)
        return response

@vpn_router.get('/config')
@error_handler
async def get_vpn_config(  # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
        request: Request, version="v2"):
    if version == "v1":
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

        # Convert string to bytes and create a BytesIO buffer
        buffer = io.BytesIO(content.encode('utf-8'))
        # Set the correct headers for downloading
        headers = {'Content-Disposition': f'attachment; filename="config_{time.time()}.yaml"'}
        return StreamingResponse(buffer, media_type='text/plain', headers=headers)

    elif version == "v2":
        target_url = "https://dist.bnsubservdom.com/api/v1/client/subscribe?token=d0a451156361a39cfd8219490f1f65ce"
        res = api.get(target_url)
        headers = res.headers
        headers = dict(headers)
        print('headers: ', headers)
        response = Response(res.content, headers=headers)
        if "transfer-encoding" in response.headers:
            del response.headers["transfer-encoding"]
        if "content-length" in response.headers:
            del response.headers["content-length"]
        return response


        # headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        #     "Referer": "https://dist.bnsubservdom.com/",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        #     "Accept-Language": "en-US,en;q=0.5",
        #     "Accept-Encoding": "gzip, deflate, br",
        #     "Connection": "keep-alive",
        #     "Upgrade-Insecure-Requests": "1",
        #     "Sec-Fetch-Dest": "document",
        #     "Sec-Fetch-Mode": "navigate",
        #     "Sec-Fetch-Site": "none",
        #     "Sec-Fetch-User": "?1",
        #     "Cache-Control": "max-age=0",
        # }
        #
        # # 合并请求的头部信息，但是我们的自定义头部优先
        # headers.update(dict(request.headers))
        #
        # try:
        #     response = await fetch_with_session(target_url, headers)
        #     response.raise_for_status()
        # except httpx.HTTPStatusError as exc:
        #     raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        # except httpx.RequestError as exc:
        #     raise HTTPException(status_code=500, detail=str(exc))
        #
        # return StreamingResponse(
        #     content=response.iter_bytes(),
        #     status_code=response.status_code,
        #     headers=dict(response.headers)
        # )
    else:
        raise Exception("no current version")
