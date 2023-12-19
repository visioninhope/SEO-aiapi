from beanie.odm.operators.find.evaluation import Text
from fastapi import APIRouter
from src.config import settings
from .dependencies import init_db
from typing import Union

from .models import Article

router = APIRouter(
    prefix='/article',
    tags = ['文章']
)

@router.get("/", summary='获取文章', description='根据关键词从数据库获取文章')
async def get(q: Union[str, None] = None):
    await init_db("ai", [Article])
    result = await Article.find(Text(q)).count()

    return {"message": result}