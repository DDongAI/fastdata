import os

from fastapi import UploadFile, HTTPException
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from config.config import settings


async def get_marker_pdf(file: UploadFile = None, user_id: str = None):
    """
    PDF OCR
    :param file:
    :param user_id:
    :return:
    """
    if not os.path.exists(f'{settings.UPLOAD_DIR}'):
        os.makedirs(f'{settings.UPLOAD_DIR}')
        print("创建临时文件夹成功")
    if not os.path.exists(f'{settings.UPLOAD_DIR}/{user_id}'):
        os.makedirs(f'{settings.UPLOAD_DIR}/{user_id}')
        print("创建临时文件夹成功")
    file_path = f"{settings.UPLOAD_DIR}/{user_id}/{file.filename}.pdf"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    # config = {
    #     "page_range": "0-15",
    #     "output_format": "markdown",
    #     "disable_image_extraction": True,
    #     "output_dir": "./output",
    #     "use_llm": True,
    #     "llm_service": "marker.services.ollama.OllamaService",
    #     "ollama_base_url": "127.0.0.1:11434",
    #     "ollama_model": "deepseek-r1:latest",
    # }
    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(file_path)
    text, _, images = text_from_rendered(rendered)

    print(text)
    return text


async def get_marker_pdf_llm(file: UploadFile = None, user_id: str = None):
    """
    PDF OCR
    :param file:
    :param user_id:
    :return:
    """
    if not os.path.exists(f'{settings.UPLOAD_DIR}'):
        os.makedirs(f'{settings.UPLOAD_DIR}')
        print("创建临时文件夹成功")
    if not os.path.exists(f'{settings.UPLOAD_DIR}/{user_id}'):
        os.makedirs(f'{settings.UPLOAD_DIR}/{user_id}')
        print(f"用户{user_id}创建临时文件夹成功")
    if not os.path.exists(f'{settings.UPLOAD_DIR}/{user_id}/output'):
        os.makedirs(f'{settings.UPLOAD_DIR}/{user_id}/output')
        print(f"用户{user_id}创建临时文件夹output成功")
    file_path = f"{settings.UPLOAD_DIR}/{user_id}/{file.filename}.pdf"
    output_dir = f'{settings.UPLOAD_DIR}/{user_id}/output'
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    config = {
        # "page_range": "0-15",
        "output_format": "markdown",
        "disable_image_extraction": True,
        "output_dir": output_dir,
        "use_llm": True,
        "llm_service": "marker.services.openai.OpenAIService",
        "openai_base_url": settings.VLLM_API_BASE,
        "openai_api_key": settings.VLLM_API_KEY,
        "openai_model": settings.VLLM_MODEL,
    }
    config_parser = ConfigParser(config)
    # converter = PdfConverter(artifact_dict=create_model_dict())
    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service()
    )
    rendered = converter(file_path)
    text, _, images = text_from_rendered(rendered)
    print(text)
    if os.path.exists(f'{settings.UPLOAD_DIR}/{user_id}'):
        try:
            # 遍历文件夹中的所有文件
            for file_name in os.listdir(f'{settings.UPLOAD_DIR}/{user_id}'):
                file_path = os.path.join(f'{settings.UPLOAD_DIR}/{user_id}', file_name)
                # 确保是文件而不是子文件夹
                if os.path.isfile(file_path):
                    os.remove(file_path)  # 删除文件
                    print(f"Deleted: {file_path}")
                for output_name in os.listdir(f'{settings.UPLOAD_DIR}/{user_id}/output'):
                    output = os.path.join(f'{settings.UPLOAD_DIR}/{user_id}', output_name)
                    os.remove(file_path)  # 删除文件
                    print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"临时文件处理中出现错误: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"临时文件处理中出现错误: {e}"
            )
    return text
