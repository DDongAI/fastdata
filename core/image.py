import io

from PIL import Image
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from config.config import settings
from core.tools import verify_file_type, image_resize_cv
from services.llm import chat_service


async def image_ocr_service(image: UploadFile = File(...)):
    # 验证图片类型
    mime_type = verify_file_type(image.filename, settings.ALLOWED_IMAGE_TYPES)
    # 读取图片内容
    image_contents = await image.read()
    # 并验证是否为有效图片
    try:
        img = Image.open(io.BytesIO(image_contents))
        # 验证图片完整性
        img.verify()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"无效的图片文件: {str(e)}"
        )
    try:
        # print(image_contents)
        # 识别图片
        bytes_data = await image_resize_cv(image_contents)
        result = await chat_service.generate_response(bytes_data)
        return result
    except HTTPException as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"服务器内部错误: {str(e)}"
        )
