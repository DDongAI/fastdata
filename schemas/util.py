from typing import Optional

from pydantic import BaseModel


class ResponseModel(BaseModel):
    """
    通用响应模型
    """
    code: int
    message: str
    data: Optional[str] = None