import os

from fastapi import UploadFile, HTTPException


# def verify_file_type(file: UploadFile, allowed_types: list):
#     """验证文件类型"""
#     # 读取文件前几字节来判断真实类型
#     content = file.file.read(1024)
#     file.file.seek(0)  # 重置文件指针
#
#     mime = magic.from_buffer(content, mime=True)
#     if mime not in allowed_types:
#         raise HTTPException(
#             status_code=400,
#             detail=f"不支持的文件类型: {mime}. 允许的类型: {', '.join(allowed_types)}"
#         )
#     return mime

def verify_file_type(filename: str, allowed_types: list):
    """根据文件名验证文件类型"""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型. 允许的扩展名: {', '.join(allowed_types)}"
        )
    return ext


def read_text_file(file: UploadFile) -> str:
    """读取文本文件内容"""
    try:
        content = file.file.read().decode("utf-8")
        return content
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="文件无法以UTF-8解码，可能不是文本文件"
        )
