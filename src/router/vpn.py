import io
import time

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from packages.common_api.index import api
from packages.common_fastapi.error_handler import error_handler

vpn_router = APIRouter(prefix='/vpn', tags=["VPN"])


@vpn_router.get('/config')
@error_handler
async def get_vpn_config_route(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
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
