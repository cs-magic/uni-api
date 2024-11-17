from fastapi import APIRouter, UploadFile, Depends, File
from sqlmodel import Session

from utils.database import get_db
from packages.fastapi.standard_error import standard_error_handler
from utils.oss import OSSClient

oss_router = APIRouter(prefix='/oss', tags=["OSS"])

oss_client = OSSClient()

# 添加一个非路由的工具函数
def upload_file_to_oss(file: UploadFile, filename: str) -> str:
    """
    直接上传文件到OSS的工具函数
    """
    return oss_client.upload_file(file, filename)

@oss_router.post('/upload')
@standard_error_handler()
async def oss_upload_file(
    file: UploadFile = File(..., description="待上传文件"),
    db: Session = Depends(get_db)
):
    oss_url = upload_file_to_oss(file, file.filename)
    return {
        "oss_url": oss_url,
        "filename": file.filename,
    }
