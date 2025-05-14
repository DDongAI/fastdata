from fastapi import APIRouter

from services.llm import chat_service

router = APIRouter()


@router.post("/chat", response_model=str)
async def generate_response(question: str, context: str):
    """
    模型对话
    """
    result = await chat_service.chat(question, context)
    return result
