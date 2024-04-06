from datetime import datetime, date

from pydantic import BaseModel as PydanticBaseMode


class BaseModel(PydanticBaseMode):
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
            date: lambda v: v.strftime('%Y-%m-%d'),
        }
