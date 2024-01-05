from beanie.odm.operators.find.evaluation import Text
from fastapi import APIRouter
from src.config import settings
from ..dependencies import init_db
from typing import Union
from bson.objectid import ObjectId
from .models import Document
from .schemas import ArticleParam

router = APIRouter(
    prefix='/document',
    tags=['文档与数据库']
)


@router.post("/", summary='录入资料',
            description='先存入 mongodb 的 documents 文档集，然后录入矢量数据库')
async def save(content: str,
                      db_name: Union[str, None] = None):
    await init_db(db_name, [Document])

    # result = await result.skip(skip).limit(limit).to_list()

    return 1
