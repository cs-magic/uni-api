import io
import time
from typing import Literal

from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse

from packages.common_api.index import api
from packages.common_fastapi.error_handler import error_handler

vpn_router = APIRouter(prefix='/vpn', tags=["VPN"])

type Provider =  Literal["foosber", "biznet"]


@vpn_router.get('/config')
@error_handler
async def get_vpn_config(  # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
        request: Request, provider: Provider = "biznet"):
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

    headers = {'Content-Disposition': f'attachment; filename="config_{time.time()}.yaml"'}
    return StreamingResponse(io.BytesIO(content.encode('utf-8')), media_type='text/plain', headers=headers)
