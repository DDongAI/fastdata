from typing import Optional

from pydantic import BaseModel


class ResponseModel(BaseModel):
    """
    通用响应模型
    """
    code: int
    message: str
    data: Optional[str] = None


class ImageSize(BaseModel):
    """
    图片大小
    """
    memory: int = 0
    pixel: int = 0
    size: int = 0
