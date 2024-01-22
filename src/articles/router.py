from beanie.odm.operators.find.evaluation import Text
from fastapi import APIRouter
from ..utils import init_db
from typing import Union
from bson.objectid import ObjectId
from .models import Article, ArticleTypeEnum
from .schemas import ArticleDeleteIn
from src.config import settings

router = APIRouter(
    prefix='/article',
    tags=['文章']
)


@router.get("/",
            summary='获取文章',
            description='根据关键词从数据库获取文章，参数列表：q, type, skip, limit, db_name。可选type为：mixed_rewrite, rewrite, original')
async def article_get(q: Union[str, None] = None,
                      skip: int = 0,
                      limit: int = 10,
                      type: Union[str, None] = None):
    await init_db(settings.db_name, [Article])

    if limit > 30: limit = 30
    result = Article.find(Text(q)) if q else Article.find({})
    if type: result = result.find({"type": type})

    total = await result.count()
    result = await result.sort(-Article.create_date).skip(skip).limit(limit).to_list()

    return {"q": q, "db_name": settings.db_name, "type": type, "types": ArticleTypeEnum.__members__.items(), "total": total, "skip": skip, "limit": limit, "data": result}




@router.post("/delete", summary='删除文章', description="根据_id删除数据集articles中的文章")
async def article_delete(body: ArticleDeleteIn):
    await init_db(body.db_name, [Article])
    result = await Article.find_one(Article.id == ObjectId(body.id)).delete()

    return {"raw_result": result.raw_result}
