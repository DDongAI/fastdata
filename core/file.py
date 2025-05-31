import io
import os
import re

import fitz
from PIL import Image
from fastapi import UploadFile, HTTPException, File

from config.config import settings
from services.llm import chat_service
from core.tools import verify_file_type, read_text_file, image_resize_cv, pdf_resize_cv, get_dir


async def pdf_ocr_service(file: str, user_id: str = ""):
    """
    PDF OCR
    :param file:
    :param user_id:
    :return:
    """
    # 获取带扩展名的文件名
    file_name_with_ext = os.path.basename(file)
    # 分割文件名和扩展名
    file_name, file_ext = os.path.splitext(file_name_with_ext)
    # 获取用户文件夹
    user_dir, upload_dir, temp_dir, result_dir = get_dir(user_id)
    # 用 fitz 打开二进制流
    pdf_document = fitz.open(file)
    print(f"PDF总页数: {len(pdf_document)}")
    result = ""
    for page_number in range(pdf_document.page_count):
        # 加载页面，将pdf的每一页转为图片
        page = pdf_document.load_page(page_number)

        pix = page.get_pixmap(dpi=300)

        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        image_file_name = f"{temp_dir}/{file_name}_page_{page_number + 1}.png"
        print(f"第{str(page_number + 1)}图片信息：{img}")
        print("开始图片保存")
        print(f"图片保存路径：{image_file_name}")

        img.save(image_file_name)

        print("图片保存成功")
        # if not os.path.exists(image_file_name):
        #     print("临时文件路径错误！")
        print(f"开始调用图片识别接口处理第{page_number + 1}页")
        # 调用图片识别接口
        # 读取文件
        # image_contents = Image.open(image_file_name)
        # print(image_contents)
        # # 使用BytesIO获取图像的二进制数据
        # bytes_data = io.BytesIO()
        # image_contents.save(bytes_data, format='PNG')  # 保存图像到BytesIO对象，格式可以是JPEG, PNG等
        # bytes_data = bytes_data.getvalue()
        bytes_data = await pdf_resize_cv(image_file_name)
        image_md = await chat_service.generate_response(bytes_data)
        image_md = re.sub(r"```markdown", "", image_md)
        image_md = re.sub(r"```(?=$|\n)", "", image_md)
        result += image_md

    # 关闭文档
    pdf_document.close()
    # 删掉临时文件
    if os.path.exists(temp_dir):
        try:
            # 遍历文件夹中的所有文件
            for temp_image_name in os.listdir(temp_dir):
                temp_image_path = os.path.join(temp_dir, temp_image_name)
                # 确保是文件而不是子文件夹
                if os.path.isfile(temp_image_path):
                    os.remove(temp_image_path)  # 删除文件
                    print(f"Deleted: {temp_image_path}")
        except Exception as e:
            print(f"临时文件处理中出现错误: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"临时文件处理中出现错误: {e}"
            )
    result_file = result_dir + f"/{file_name}.md"
    with open(result_file, 'w', encoding='utf-8') as file:
        file.write(result)
    return result


async def get_status(user_id: str):
    """
    查询文件清洗状态
    :param user_id:
    :return:
    """
    # 获取用户文件夹
    user_dir, upload_dir, temp_dir, result_dir = get_dir(user_id)
    if not os.path.exists(upload_dir) or not os.path.exists(result_dir):
        return 0, None
    # 上传集
    # files_list = os.listdir(upload_dir)
    files_list = [os.path.splitext(f)[0] for f in os.listdir(upload_dir)]

    # 结果集
    # result_list = os.listdir(result_dir)
    result_list = [os.path.splitext(f)[0] for f in os.listdir(result_dir)]

    result = dict.fromkeys(files_list, False)

    for file in result_list:
        result[file] = True

    if False in result.values():
        return 1, result
    else:
        return 2, result
