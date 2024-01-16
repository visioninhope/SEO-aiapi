from beanie.odm.operators.find.evaluation import Text
from fastapi import APIRouter
from src.config import settings
from ..utils import init_db
from typing import Union
from bson.objectid import ObjectId



router = APIRouter(
    prefix='/document',
    tags=['文档与数据库']
)


@router.get("/",
            response_model=DocumentListOut,
            summary='获取资料列表',
            description='获取可选数据库列表，否定词列表，该数据库已录入总数')
async def document_get(q: Union[str, None] = None,
                       source: Union[str, None] = None,
                       skip: int = 0,
                       limit: int = 10,
                       db_name: Union[str, None] = None):
    await init_db(db_name, [DocumentTest, Config])
    # 获取资料列表与总数
    if limit > 30: limit = 30
    result = DocumentTest.find(Text(q)) if q else DocumentTest.find({})
    if source: result = DocumentTest.find({"source": source})
    total = await result.count()
    result = await result.sort(-DocumentTest.create_date).skip(skip).limit(limit).to_list()

    # 获取否定关键词列表
    negative_keywords = await Config.find_one(Config.key == 'negative_keywords')

    return {"q": q,"db_name": db_name, "source": source, "total": total, "skip": skip, "limit": limit, "data": result, "chunk_size": settings.chunk_size, "negative_keywords": negative_keywords.value}


@router.post("/delete", response_model=DBResultOut, summary='删除该资料', description="根据资料_id删除该资料，并同步删除矢量数据库中的同源数据")
async def document_delete(body: DocumentDeleteIn):
    delete_from_chroma_by_source(body.source)

    # mongodb中删除记录
    await init_db(body.db_name, [DocumentTest])
    result = await DocumentTest.find_one(DocumentTest.id == ObjectId(body.id)).delete()

    return {"raw_result": result.raw_result}
