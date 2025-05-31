# import openai
import base64

from openai import AsyncOpenAI

from config.config import settings
from tenacity import retry, stop_after_attempt, wait_fixed

class ChatService:
    def __init__(self):
        # 配置vLLM API
        # self.api_key = settings.CHAT_API_KEY
        # self.api_base = settings.CHAT_API_BASE
        # self.model = settings.CHAT_MODEL
        self.api_key = settings.VLLM_API_KEY
        self.api_base = settings.VLLM_API_BASE
        self.model = settings.VLLM_MODEL

    async def chat(self, question: str, context: str) -> str:
        """
        对话
        """
        try:
            messages = [
                {"role": "system", "content": "你是一个很有用的助手，根据上下文回答用户的问题"},
                {"role": "user", "content": f"上下文信息：\n{context}\n\n用户问题：{question}"}
            ]

            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                timeout=100
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"生成回复失败: {str(e)}")

    # @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def generate_response(self, image_contents: bytes) -> str:
        """
        openai大模型图像识别
        """
        try:
            # 将二进制文件转成字节码
            base64_image = base64.b64encode(image_contents).decode("utf-8")
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": settings.MY_PROMPT_VL_SYSTEM,
                        },
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": settings.MY_PROMPT_VL_USER,
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                },
            ]

            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=4096,
                timeout=180
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"生成回复失败: {str(e)}")


chat_service = ChatService()
