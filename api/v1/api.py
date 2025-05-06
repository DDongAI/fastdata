from fastapi import APIRouter

from api.v1 import file, image, chat

api_router = APIRouter()

api_router.include_router(file.router, prefix="/file", tags=["file"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
