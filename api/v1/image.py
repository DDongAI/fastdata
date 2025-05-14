import io
import os
import re

from PIL import Image
from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from config.config import settings
from core.tools import verify_file_type, read_text_file, process_str
from core.image import image_ocr_service
from schemas.util import ResponseModel
from services.llm import chat_service

router = APIRouter()


@router.post("/upload", response_model=ResponseModel)
async def upload_image(image: UploadFile = File(...)):
    """
    上传图片
    :param image:
    :return:
    """
    if not image:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "文件错误",
                "data": ""
            }
        )
    # 验证图片大小
    if image.size > settings.MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": f"文件大小超出限制. 最大允许大小: 5M",
                "data": None
            }
        )
    try:
        result = await image_ocr_service(image)
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": f"success",
                "data": f"{result}"
            }
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "code": e.status_code,
                "message": e.detail,
                "data": None
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"服务器内部错误: {str(e)}",
                "data": None
            }
        )


@router.post("/download")
async def download(image_str: str = ""):
    """
    下载文件
    :param image_str:
    :return:
    """
    if not image_str or image_str == " " or image_str == "" or image_str is None:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "文件错误",
                "data": None
            }
        )


    try:
        file_stream = io.BytesIO(image_str.encode("utf-8"))  # \\r\\n
        # file_stream = io.StringIO(image_str)
        # str1 = f"""# 第一行{os.linesep}# 第二行{os.linesep}# 第三行"""
        # print(image_str)
        normalized_content = await process_str(image_str)
        # print(file_stream.getvalue())
        # print(normalized_content)
        # with open('uploads/example.md', 'w', encoding='utf-8') as f:
        #     f.write(normalized_content)
        return StreamingResponse(
            content=normalized_content,
            media_type="text/markdown; charset=utf-8",
            # media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=file.md",
                "Content-Type": "text/markdown; charset=utf-8"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"服务器内部错误: {str(e)}",
                "data": None
            }
        )

