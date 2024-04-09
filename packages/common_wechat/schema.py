from typing import Literal, Optional

from packages.common_common.pydantic import BaseModel


class WechatMessageUrlModel(BaseModel):
    type: Literal["wxmp-article", "wxmp-video", "default"] = "default"
    url: Optional[str] = None
    raw: Optional[str] = None
