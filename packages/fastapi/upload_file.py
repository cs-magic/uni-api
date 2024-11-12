from fastapi import UploadFile

from packages.common.upload_file import UploadFileInfo


async def convert_to_upload_file_info(upload_file: UploadFile) -> UploadFileInfo:
    """Convert FastAPI UploadFile to UploadFileInfo"""
    content = await upload_file.read()
    try:
        return UploadFileInfo(
            filename=upload_file.filename,
            content=content,
            content_type=upload_file.content_type
        )
    finally:
        await upload_file.seek(0)  # Reset file pointer for potential future reads
