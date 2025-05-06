import io

from PIL import Image
from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from config.config import settings
from core.file import verify_file_type
from schemas.util import ResponseModel

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

    # 读取图片内容
    contents = await image.read()
    # 验证图片大小
    if len(contents) > settings.MAX_FILE_SIZE:
        # raise HTTPException(
        #     status_code=400,
        #     detail=f"文件大小超出限制. 最大允许大小: {settings.MAX_FILE_SIZE} bytes"
        # )
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": f"文件大小超出限制. 最大允许大小: {settings.MAX_FILE_SIZE} bytes",
                "data": None
            }
        )
    # 并验证是否为有效图片
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()  # 验证图片完整性
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"无效的图片文件: {str(e)}"
        )

    try:
        print(img)
        # 这里可以添加保存图片的逻辑
        # 例如:
        # contents = await image.read()
        # with open(f"uploads/{image.filename}", "wb") as f:
        #     f.write(contents)

        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": f"图片上传成功，类型: {mime_type}",
                "data": f"图片名称: {image.filename}"
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
