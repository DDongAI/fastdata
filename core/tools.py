import os
import re

from fastapi import UploadFile, HTTPException


def verify_file_type(filename: str, allowed_types: list):
    """根据文件名验证文件类型
    :param filename:
    :param allowed_types:
    :return:
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型. 允许的扩展名: {', '.join(allowed_types)}"
        )
    return ext


def read_text_file(file: UploadFile) -> str:
    """读取文本文件内容
    :param file:
    :return:
    """
    try:
        content = file.file.read().decode("utf-8")
        return content
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="文件无法以UTF-8解码，可能不是文本文件"
        )


async def process_str(text: str) -> str:
    """
    处理字符串
    :param text:
    :return:
    """
    if text == "" or text == " ":
        return text
    n: str = os.linesep
    normalized_content = re.sub(r"\\r\\n", n, text)
    normalized_content = re.sub(r"\\n", n, normalized_content)
    normalized_content = re.sub(r"(?<=^)```markdown", "", normalized_content)
    normalized_content = re.sub(r"```(?=$)", "", normalized_content)

    return normalized_content

