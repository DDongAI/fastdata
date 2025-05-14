import io
import os
import re

import fitz
from PIL import Image
from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from config.config import settings
from core.file import pdf_ocr_service
from core.tools import verify_file_type, read_text_file, process_str
from schemas.util import ResponseModel
from services.llm import chat_service

router = APIRouter()


@router.post("/upload", response_model=ResponseModel)
async def upload_file(file: UploadFile = File(...), user_id: str = ""):
    """
    上传文件
    :param file:
    :param user_id:
    :return:
    """
    if not file:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "文件错误",
                "data": " "
            }
        )
    if not user_id or user_id == "" or user_id is None or user_id == " ":
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "用户ID错误",
                "data": " "
            }
        )
    # 验证文件类型
    try:
        type = verify_file_type(file.filename, settings.PDF)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": f"文件类型错误，支持格式：{settings.PDF}",
                "data": None
            }
        )
    try:
        result, mime_type = await pdf_ocr_service(file, user_id)
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": f"success，文件类型: {mime_type}",
                "data": f"```markdown\n{result}\n```"
            }
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "code": e.status_code,
                "message": e.detail,
                "data": " "
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"服务器内部错误: {str(e)}",
                "data": " "
            }
        )


@router.post("/download")
async def download(pdf_str: str = ""):
    """
    下载文件
    :param pdf_str:
    :return:
    """
    if not pdf_str or pdf_str == " " or pdf_str == "" or pdf_str is None:
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "文件错误",
                "data": " "
            }
        )
    try:
        file_stream = io.BytesIO(pdf_str.encode("utf-8"))
        normalized_content = await process_str(pdf_str)
        return StreamingResponse(
            normalized_content,
            media_type="text/markdown; charset=utf-8",
            # media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=example.md",
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
