import io
import time

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from packages.common_api.index import api
from packages.common_fastapi.error_handler import error_handler

vpn_router = APIRouter(prefix='/vpn', tags=["VPN"])


@vpn_router.get('/config')
@error_handler
async def get_config(
    # user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    content_raw = api.get('https://xn--eckvarq8ld5k.xn--zckq7gxe.xn--tckwe/link/4lHIflFQQsH1S8qM?clash=1').text
    
    domain = 'linkedin.com'
    router_from = 'DIRECT'
    router_to = '🔰 国外流量'
    content = content_raw.replace(f'{domain},{router_from}', f'{domain},{router_to}')
    
    # Convert string to bytes and create a BytesIO buffer
    buffer = io.BytesIO(content.encode('utf-8'))
    # Set the correct headers for downloading
    headers = {'Content-Disposition': f'attachment; filename="config_{time.time()}.yaml"'}
    return StreamingResponse(buffer, media_type='text/plain', headers=headers)
