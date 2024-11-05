from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel



class PusherContent(BaseModel):
    text: str
    images: Optional[List[UploadFile]] = []
