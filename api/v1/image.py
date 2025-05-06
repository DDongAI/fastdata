import io

from PIL import Image
from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from config.config import settings
from core.file import verify_file_type
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
    # 验证图片类型
    mime_type = verify_file_type(image.filename, settings.ALLOWED_IMAGE_TYPES)
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
    # 读取图片内容
    image_contents = await image.read()
    # 并验证是否为有效图片
    try:
        img = Image.open(io.BytesIO(image_contents))
        img.verify()  # 验证图片完整性
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"无效的图片文件: {str(e)}"
        )
    try:
        # print(image_contents)
        # 识别图片
        result = await chat_service.generate_response(image_contents)
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
