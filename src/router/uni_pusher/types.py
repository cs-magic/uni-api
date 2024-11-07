from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel



class PushContent(BaseModel):
    text: str
    images: Optional[List[UploadFile]] = []


class JikePushContent(PushContent):
    submitToTopic: Optional[str] = None
    syncToPersonalUpdate: bool = True
