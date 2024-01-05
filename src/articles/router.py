from beanie.odm.operators.find.evaluation import Text
from fastapi import APIRouter
from src.config import settings
from .dependencies import init_db
from typing import Union
from bson.objectid import ObjectId
from .models import Article, ArticleTest
from .schemas import ArticleParam

router = APIRouter(
    prefix='/article',
    tags=['文章']
)


@router.get("/", summary='获取文章',
            description='根据关键词从数据库获取文章，参数列表：q, type, skip, limit, db_name。可选type为：mixed_rewrite, rewrite, original')
async def article_get(q: Union[str, None] = None,
                      type: Union[str, None] = None,
                      skip: Union[int, None] = 0,
                      limit: Union[int, None] = 10,
                      db_name: Union[str, None] = None):
    if not db_name: db_name = settings.db_name
    await init_db(db_name, [Article])

    if q:
        result = Article.find(Text(q))
    else:
        result = Article.find({})

    if type:
        result = result.find({"type": type})

    total = await result.count()
    result = await result.skip(skip).limit(limit).to_list()

    return {"db_name": db_name, "type": type, "total": total, "skip": skip, "limit": limit, "contents": result}

@router.post("/delete", summary='删除文章', description="根据_id删除数据集articles中的文章")
async def article_delete(body: ArticleParam):
    await init_db(body.db_name, [Article])
    result = await Article.find_one(Article.id == ObjectId(body.id)).delete()

    return {"deleted_count": result.deleted_count, "raw_result": result.raw_result}
