from fastapi import APIRouter

from services.llm import chat_service

router = APIRouter()


@router.post("/chat", response_model=str)
async def generate_response(question: str, context: str):
    """
    openai大模型图像识别
    """
    result = await chat_service.generate_response(question, context)
    return result