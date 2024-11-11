from typing import Optional

from fastapi import UploadFile


class UploadFileInfo:
    """Generic file upload container that doesn't depend on any web framework"""

    def __init__(self, filename: str, content: bytes, content_type: Optional[str] = None):
        self.filename = filename
        self.content = content
        self.content_type = content_type or "application/octet-stream"


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
