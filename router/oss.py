from fastapi import APIRouter, UploadFile, Depends, File
from sqlmodel import Session

from utils.database import get_db
from packages.fastapi.standard_error import standard_error_handler
from utils.oss import OSSClient

oss_router = APIRouter(prefix='/oss', tags=["OSS"])


oss_client = OSSClient()


@oss_router.post('/upload')
@standard_error_handler()
async def oss_upload_file(# user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
    file: UploadFile = File(..., description="待上传文件"),
    db: Session = Depends(get_db)
):
    oss_url = oss_client.upload_file(file, file.filename)
    return {
        "oss_url": oss_url,
        "filename": file.filename,
    }
