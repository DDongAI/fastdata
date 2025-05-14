import io
import os
import re

import fitz
from PIL import Image
from fastapi import UploadFile, HTTPException, File

from config.config import settings
from services.llm import chat_service
from core.tools import verify_file_type,read_text_file


async def pdf_ocr_service(file: UploadFile = File(...), user_id: str = ""):
    """
    PDF OCR
    :param file:
    :param user_id:
    :return:
    """
    # 验证文件类型
    try:
        mime_type = verify_file_type(file.filename, settings.PDF)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型. 允许的扩展名: {', '.join(settings.PDF)}"
        )
    # 打开文件
    contents = await file.read()
    # 用 fitz 打开二进制流
    pdf_document = fitz.open(stream=contents, filetype="pdf")
    print(f"PDF总页数: {len(pdf_document)}")
    result = ""
    for page_number in range(pdf_document.page_count):
        # 加载页面，将pdf的每一页转为图片
        page = pdf_document.load_page(page_number)

        pix = page.get_pixmap(dpi=300)

        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        if not os.path.exists(f'{settings.UPLOAD_DIR}'):
            os.makedirs(f'{settings.UPLOAD_DIR}')
            print("创建临时文件夹成功")
        if not os.path.exists(f'{settings.UPLOAD_DIR}/{user_id}'):
            os.makedirs(f'{settings.UPLOAD_DIR}/{user_id}')
            print("创建临时文件夹成功")

        image_file_name = f"{settings.UPLOAD_DIR}/{user_id}/{file.filename}_page_{page_number + 1}.png"

        print(f"第{str(page_number + 1)}图片信息：{img}")
        print("开始图片保存")
        print(f"图片保存路径：{image_file_name}")

        img.save(image_file_name)

        print("图片保存成功")
        if not os.path.exists(image_file_name):
            print("临时文件路径错误！")

        print(f"开始调用图片识别接口处理第{page_number + 1}页")
        # 调用图片识别接口
        # 读取文件
        image_contents = Image.open(image_file_name)
        print(image_contents)
        # 使用BytesIO获取图像的二进制数据
        bytes_data = io.BytesIO()
        image_contents.save(bytes_data, format='PNG')  # 保存图像到BytesIO对象，格式可以是JPEG, PNG等
        bytes_data = bytes_data.getvalue()
        image_md = await chat_service.generate_response(bytes_data)
        image_md = re.sub(r"```markdown", "", image_md)
        image_md = re.sub(r"```(?=$|\n)", "", image_md)
        result += image_md

    # 关闭文档
    pdf_document.close()
    # 删掉临时文件
    if os.path.exists(f'{settings.UPLOAD_DIR}/{user_id}'):
        try:
            # 遍历文件夹中的所有文件
            for file_name in os.listdir(f'{settings.UPLOAD_DIR}/{user_id}'):
                file_path = os.path.join(f'{settings.UPLOAD_DIR}/{user_id}', file_name)
                # 确保是文件而不是子文件夹
                if os.path.isfile(file_path):
                    os.remove(file_path)  # 删除文件
                    print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"临时文件处理中出现错误: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"临时文件处理中出现错误: {e}"
            )
    return result, mime_type
