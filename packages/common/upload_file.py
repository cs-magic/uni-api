from typing import Optional


class UploadFileInfo:
    """Generic file upload container that doesn't depend on any web framework"""

    def __init__(self, filename: str, content: bytes, content_type: Optional[str] = None):
        self.filename = filename
        self.content = content
        self.content_type = content_type or "application/octet-stream"
