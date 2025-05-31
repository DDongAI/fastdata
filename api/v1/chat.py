from fastapi import APIRouter

from schemas.util import ChatModel
from services.llm import chat_service

router = APIRouter()


@router.post("/chat", response_model=str)
async def generate_response(message: ChatModel = None):
    """
    模型对话 \n
    输入问题和上下文内容，返回模型的回复 \n
    """
    result = await chat_service.chat(message.question, message.context)
    return result
