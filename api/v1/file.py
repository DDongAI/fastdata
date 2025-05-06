from fastapi import APIRouter
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from config.config import settings
from core.file import verify_file_type, read_text_file
from schemas.util import ResponseModel

router = APIRouter()


@router.post("/upload", response_model=ResponseModel)
async def upload_file(file: UploadFile = File(...)):
    try:
        # 验证文件类型
        mime_type = verify_file_type(file.filename, settings.PDF)

        # 如果是文本文件，读取内容
        if mime_type == "text/plain":
            content = read_text_file(file)
        else:
            content = "非文本文件内容未读取"

        # 这里可以添加保存文件的逻辑
        # 例如:
        # contents = await file.read()
        # with open(f"uploads/{file.filename}", "wb") as f:
        #     f.write(contents)

        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "message": f"文件上传成功，类型: {mime_type}",
                "data": content if mime_type == "text/plain" else f"文件名称: {file.filename}"
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
