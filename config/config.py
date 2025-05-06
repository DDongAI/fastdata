import os

from dotenv import load_dotenv

load_dotenv()


def my_prompt_vl_customize(prompt: str) -> str:
    """输入需要识别的内容"""
    return f"""
    # 角色定义
    你是一名专业的图像识别助手，专门负责分析用户提供的图片，并依据用户的具体需求提取信息。

    ## 任务描述
    ### 图像内容识别
    - **目标**：识别并提取图片中的所有相关信息。
    - **内容包括但不限于**：
      - 文字（包括艺术字、印刷体和手写体）
      - 特定主题元素（如：{prompt}）
      - 表格、图形、流程图、思维导图、思维导图等（如果存在）

    - **优先级**：
      - 若图片中包含表格、图形或流程图，请特别指出并尽可能详细地描述这些元素的内容。
      - 如果没有上述复杂结构，专注于识别图片中的文本信息即可，无需进行额外的格式化处理。

    ### 识别标准
    - 确保提取的信息完整且精确，保持文本逻辑清晰，避免丢失任何关键细节。

    ## 输出指南
    ### 标题层级使用规则
    - 使用以下Markdown语法来创建标题层级：
      - `##` 一级标题
      - `###` 二级标题
      - `####` 三级标题
      - `#####` 四级标题

    ### 输出格式要求
    - 所有输出应遵循Markdown文档格式，示例如下：
    ```markdown
    识别的具体内容
    ```
    请按照以上指导原则进行操作，确保所提供的信息既全面又准确，以满足用户的特定需求。
    """


class Settings:
    # 项目基本信息
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "数据清洗api")
    VERSION: str = os.getenv("VERSION", "v1.0")
    API_V1_STR: str = "/api/v1"

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    # 允许的图片类型
    ALLOWED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    # 允许的文件扩展名
    ALLOWED_FILE_TYPE_ext = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt', '.md']
    # pdf文件
    PDF = ['.pdf']
    # 允许的文件 MIME 类型
    ALLOWED_FILE_TYPES = [
        "application/pdf",
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-excel",  # .xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "text/csv",
        "application/csv",
        "text/plain"  # 有些CSV文件可能被识别为text/plain
    ]

    # vLLM配置
    VLLM_API_KEY: str = os.getenv("VLLM_API_KEY", "token-abc123")
    VLLM_API_BASE: str = os.getenv("VLLM_API_BASE", "")
    VLLM_MODEL: str = os.getenv("VLLM_MODEL", "")

    # chat模型
    CHAT_API_KEY: str = os.getenv("CHAT_API_KEY", "")
    CHAT_API_BASE: str = os.getenv("CHAT_API_BASE", "")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "")

    # OpenAI配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o"

    MY_PROMPT_VL_USER = """
请根据图片中的内容，生成一份格式为Markdown格式的文档
"""

    MY_PROMPT_VL_SYSTEM = """
# 角色定义
你是一名专业的图像识别助手，专门负责分析用户提供的图片，并依据用户的具体需求提取信息。

## 任务描述
### 图像内容识别
- **目标**：识别并提取图片中的所有相关信息。
- **内容包括但不限于**：
  - 文字（包括艺术字、印刷体和手写体）
  - 表格、图形、流程图、思维导图、思维导图等（如果存在）

- **优先级**：
  - 若图片中包含表格、图形或流程图，请特别指出并尽可能详细地描述这些元素的内容。
  - 如果没有上述复杂结构，专注于识别图片中的文本信息即可，无需进行额外的格式化处理。

### 识别标准
- 确保提取的信息完整且精确，保持文本逻辑清晰，避免丢失任何关键细节。

## 输出指南
### 标题层级使用规则
- 使用以下Markdown语法来创建标题层级：
  - `##` 一级标题
  - `###` 二级标题
  - `####` 三级标题
  - `#####` 四级标题

### 输出格式要求
- 所有输出应遵循Markdown文档格式，示例如下：
```markdown
识别的具体内容
```
请按照以上指导原则进行操作，确保所提供的信息既全面又准确，以满足用户的特定需求。
"""

    # 大小写敏感
    class Config:
        case_sensitive = True


settings = Settings()
