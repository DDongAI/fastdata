import io
import math
import os
import re
import shutil
from asyncio import sleep

import cv2
import numpy as np
from PIL import Image
from fastapi import UploadFile, HTTPException

from config.config import settings


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


async def image_resize_cv(upload_file, target_kb=400, quality=85, min_scale=0.1):
    """
    使用OpenCV降低图片分辨率至目标大小以下
    :param upload_file: PIL Image对象
    :param target_kb: 目标大小(KB)
    :param quality: 保存质量(1-100)
    :param min_scale: 最小缩放比例
    :return: 处理后的PIL Image对象
    """
    img = Image.open(io.BytesIO(upload_file))
    # 将PIL图像转换为OpenCV格式
    opencv_image = np.array(img)
    # 转换颜色空间(RGB->BGR)
    if len(opencv_image.shape) == 3 and opencv_image.shape[2] == 3:
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)

    # 检查原始大小
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    # 确保图像是 uint8 类型，并且是 2D/3D 数组
    if not isinstance(opencv_image, np.ndarray):
        raise ValueError("输入图像必须是 NumPy 数组")

    if opencv_image.dtype != np.uint8:
        opencv_image = opencv_image.astype(np.uint8)

    # 如果是带透明通道的图像 (4通道)，则移除 alpha 通道
    if len(opencv_image.shape) == 3 and opencv_image.shape[2] == 4:
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGRA2BGR)

    # 再次确认 shape 是否有效
    if len(opencv_image.shape) not in [2, 3]:
        raise ValueError("图像维度不合法，请确保是灰度图或三通道彩色图")
    _, buffer = cv2.imencode('.jpg', opencv_image, encode_param)
    original_size_kb = len(buffer) / 1024

    if original_size_kb <= target_kb:
        print(f"图片已小于{target_kb}KB，无需调整。大小: {original_size_kb:.2f}KB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format or 'JPEG')
        img_bytes = img_byte_arr.getvalue()
        return img_bytes

    print(f"原始图片大小: {original_size_kb:.2f}KB，开始压缩...")

    height, width = opencv_image.shape[:2]
    scale = 1.0
    last_valid_img = None
    last_valid_scale = 1.0

    # progress_bar = st.progress(0)
    # status_text = st.empty()

    # 计算初始缩放比例
    initial_scale = math.sqrt(target_kb / original_size_kb)
    scale = max(initial_scale * 0.9, min_scale)

    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        progress = attempts / max_attempts
        # progress_bar.progress(min(progress, 1.0))

        # 计算新尺寸
        new_width = int(width * scale)
        new_height = int(height * scale)

        # 缩放图像(使用INTER_AREA插值-最适合缩小)
        resized_img = cv2.resize(
            opencv_image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

        # 检查大小
        _, buffer = cv2.imencode('.jpg', resized_img, encode_param)
        current_size_kb = len(buffer) / 1024

        # status_text.text(f"尝试 {attempts}/{max_attempts}: 比例 {scale:.2f}, 大小 {current_size_kb:.2f}KB")

        if current_size_kb <= target_kb:
            last_valid_img = resized_img
            last_valid_scale = scale
            if scale >= 0.95:
                break
            scale = min(scale * 1.05, 1.0)
        else:
            if last_valid_img is not None:
                break
            scale *= 0.9
            if scale < min_scale:
                scale = min_scale
                new_width = int(width * scale)
                new_height = int(height * scale)
                resized_img = cv2.resize(
                    opencv_image,
                    (new_width, new_height),
                    interpolation=cv2.INTER_AREA
                )
                last_valid_img = resized_img
                break

    # progress_bar.empty()
    # status_text.empty()

    if last_valid_img is not None:
        # 转换回PIL格式
        if len(last_valid_img.shape) == 3 and last_valid_img.shape[2] == 3:
            last_valid_img = cv2.cvtColor(last_valid_img, cv2.COLOR_BGR2RGB)
        processed_img = Image.fromarray(last_valid_img)

        # 计算最终大小
        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='JPEG', quality=quality)
        final_size_kb = len(img_byte_arr.getvalue()) / 1024

        print(f"压缩完成! 最终大小: {final_size_kb:.2f}KB, 缩放比例: {last_valid_scale:.2f}")

        return img_byte_arr.getvalue()
    else:
        print("无法将图片压缩到目标大小以下")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format or 'JPEG')
        img_bytes = img_byte_arr.getvalue()
        return img_bytes


async def pdf_resize_cv(input_path, target_kb=400, quality=85, min_scale=0.1):
    """
    使用OpenCV降低图片分辨率至目标大小以下
    :param input_path: PIL Image对象路径
    :param target_kb: 目标大小(KB)
    :param quality: 保存质量(1-100)
    :param min_scale: 最小缩放比例
    :return: 处理后的PIL Image对象
    """
    img = Image.open(input_path)
    # 将PIL图像转换为OpenCV格式
    opencv_image = np.array(img)
    # 转换颜色空间(RGB->BGR)
    if len(opencv_image.shape) == 3 and opencv_image.shape[2] == 3:
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)

    # 检查原始大小
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    # 确保图像是 uint8 类型，并且是 2D/3D 数组
    if not isinstance(opencv_image, np.ndarray):
        raise ValueError("输入图像必须是 NumPy 数组")

    if opencv_image.dtype != np.uint8:
        opencv_image = opencv_image.astype(np.uint8)

    # 如果是带透明通道的图像 (4通道)，则移除 alpha 通道
    if len(opencv_image.shape) == 3 and opencv_image.shape[2] == 4:
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGRA2BGR)

    # 再次确认 shape 是否有效
    if len(opencv_image.shape) not in [2, 3]:
        raise ValueError("图像维度不合法，请确保是灰度图或三通道彩色图")
    _, buffer = cv2.imencode('.jpg', opencv_image, encode_param)
    original_size_kb = len(buffer) / 1024

    if original_size_kb <= target_kb:
        print(f"图片已小于{target_kb}KB，无需调整。大小: {original_size_kb:.2f}KB")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format or 'JPEG')
        img_bytes = img_byte_arr.getvalue()
        return img_bytes

    print(f"原始图片大小: {original_size_kb:.2f}KB，开始压缩...")

    height, width = opencv_image.shape[:2]
    scale = 1.0
    last_valid_img = None
    last_valid_scale = 1.0

    # progress_bar = st.progress(0)
    # status_text = st.empty()

    # 计算初始缩放比例
    initial_scale = math.sqrt(target_kb / original_size_kb)
    scale = max(initial_scale * 0.9, min_scale)

    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        # progress = attempts / max_attempts
        # progress_bar.progress(min(progress, 1.0))

        # 计算新尺寸
        new_width = int(width * scale)
        new_height = int(height * scale)

        # 缩放图像(使用INTER_AREA插值-最适合缩小)
        resized_img = cv2.resize(
            opencv_image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

        # 检查大小
        _, buffer = cv2.imencode('.jpg', resized_img, encode_param)
        current_size_kb = len(buffer) / 1024

        # status_text.text(f"尝试 {attempts}/{max_attempts}: 比例 {scale:.2f}, 大小 {current_size_kb:.2f}KB")

        if current_size_kb <= target_kb:
            last_valid_img = resized_img
            last_valid_scale = scale
            if scale >= 0.95:
                break
            scale = min(scale * 1.05, 1.0)
        else:
            if last_valid_img is not None:
                break
            scale *= 0.9
            if scale < min_scale:
                scale = min_scale
                new_width = int(width * scale)
                new_height = int(height * scale)
                resized_img = cv2.resize(
                    opencv_image,
                    (new_width, new_height),
                    interpolation=cv2.INTER_AREA
                )
                last_valid_img = resized_img
                break

    # progress_bar.empty()
    # status_text.empty()

    if last_valid_img is not None:
        # 转换回PIL格式
        if len(last_valid_img.shape) == 3 and last_valid_img.shape[2] == 3:
            last_valid_img = cv2.cvtColor(last_valid_img, cv2.COLOR_BGR2RGB)
        processed_img = Image.fromarray(last_valid_img)

        # 计算最终大小
        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='JPEG', quality=quality)
        final_size_kb = len(img_byte_arr.getvalue()) / 1024

        print(f"压缩完成! 最终大小: {final_size_kb:.2f}KB, 缩放比例: {last_valid_scale:.2f}")

        return img_byte_arr.getvalue()
    else:
        print("无法将图片压缩到目标大小以下")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format or 'JPEG')
        img_bytes = img_byte_arr.getvalue()
        return img_bytes


async def save_file(file: UploadFile, user_id: str = "") -> str:
    """
    保存上传的文件
    :param file:
    :param user_id:
    :return: 保存后的文件路径
    """
    # 构建文件保存路径
    upload_dir, temp_dir, result_dir = await create_dir(user_id)
    file_path = os.path.join(upload_dir, file.filename)

    if os.path.exists(file_path):
        print(f"文件已存在，删除旧文件: {file_path}")
        os.remove(file_path)
        result_path = result_dir + "/" + os.path.splitext(file.filename)[0] + ".md"
        if os.path.exists(result_path):
            os.remove(result_path)
            print(f"删除旧文件: {result_path}")

    # 保存文件到本地
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()  # 读取文件内容
            buffer.write(content)  # 写入文件到本地
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传时文件保存失败: {str(e)}")
    await sleep(1)
    return file_path


async def create_dir(user_id: str):
    """
    创建用户文件夹
    :param user_id:
    :return:
    """
    user_dir, upload_dir, temp_dir, result_dir = get_dir(user_id)
    if not os.path.exists(f'{settings.UPLOAD_DIR}'):
        os.makedirs(f'{settings.UPLOAD_DIR}')
        print(f"创建文件夹 {settings.UPLOAD_DIR} 成功")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        print(f"创建 {user_id} 文件夹成功")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        print("创建 temp 文件夹成功")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
        print("创建 result 文件夹成功")
    # os.makedirs(upload_dir, exist_ok=True)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print("创建 upload 文件夹成功")
    return upload_dir, temp_dir, result_dir


def get_dir(user_id: str):
    """
    获取用户文件夹
    :param user_id:
    :return:
    """
    upload_dir = f"{settings.UPLOAD_DIR}/{user_id}/upload"
    result_dir = f"{settings.UPLOAD_DIR}/{user_id}/result"
    temp_dir = f"{settings.UPLOAD_DIR}/{user_id}/temp"
    user_dir = f"{settings.UPLOAD_DIR}/{user_id}"

    return user_dir, upload_dir, temp_dir, result_dir


async def delete_dir(del_dir: str):
    """
    删除文件夹，递归删除整个文件夹及其内容
    :param del_dir:
    :return:
    """
    if not os.path.exists(del_dir):
        print(f"路径不存在: {del_dir}")
        return

    try:
        shutil.rmtree(del_dir)
        print(f"成功删除文件夹: {del_dir}")
    except Exception as e:
        print(f"删除文件夹失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除文件夹失败: {str(e)}")


async def read_md(file_name: str, user_id: str = ""):
    """
    读取md文件，不带后缀名
    :param file_name:
    :param user_id:
    :return:
    """
    user_dir, upload_dir, temp_dir, result_dir = get_dir(user_id)
    # read_dir = os.path.join(result_dir, file_name)
    # 文件名不带后缀名
    result_file = f"{result_dir}/{file_name}.md"
    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail=f"文件不存在或未清洗完成: {file_name}")
    with open(result_file, 'r', encoding='utf-8') as file:
        content = file.read()
    return "```markdown" + content + "```"
