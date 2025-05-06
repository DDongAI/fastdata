# import openai
from openai import AsyncOpenAI

from config.config import settings


class ChatService:
    def __init__(self):
        # 配置vLLM API
        # self.api_key = settings.CHAT_API_KEY
        # self.api_base = settings.CHAT_API_BASE
        # self.model = settings.CHAT_MODEL
        self.api_key = settings.VLLM_API_KEY
        self.api_base = settings.VLLM_API_BASE
        self.model = settings.VLLM_MODEL
        self.system_prompt = """你是一个智能助手，基于用户上传的文档内容回答问题。
请根据提供的上下文信息，给出准确、简洁的回答。
如果问题与文档内容无关，请礼貌地告知用户。
回答时请使用中文。"""

    async def generate_response(
            self,
            question: str,
            context: str,
    ) -> str:
        """
        openai大模型图像识别
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
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
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"生成回复失败: {str(e)}")


chat_service = ChatService()

# result = asyncio.run(chat_service.generate_response("你好", "这是一个上下文", 1))