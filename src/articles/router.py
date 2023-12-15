from fastapi import APIRouter
from src.config import settings

router = APIRouter(
    prefix='/article',
    tags = ['article']
)

@router.get("/", summary='获取文章', description='根据关键词从数据库获取文章')
def get() -> dict:
    return {"message": settings.openai_key}