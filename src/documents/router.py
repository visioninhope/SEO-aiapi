from beanie.odm.operators.find.evaluation import Text
from fastapi import APIRouter
from src.config import settings
from ..dependencies import init_db
from typing import Union
from bson.objectid import ObjectId
from .models import Document, DocumentTest
from .schemas import DocumentParam

router = APIRouter(
    prefix='/document',
    tags=['文档与数据库']
)


@router.get("/", summary='资料管理页',
            description='获取可选数据库列表，否定词列表，该数据库已录入总数')
async def document_get(q: Union[str, None] = None,
                      source: Union[str, None] = None,
                      skip: Union[int, str] = 0,
                      limit: Union[int, str] = 10,
                      db_name: Union[str, None] = None):
    await init_db(db_name, [DocumentTest])

    # 转换接收的字符串为数字
    if skip=="": skip = 0
    else: skip = int(skip)
    if limit=="": limit = 10
    else: limit = int(limit)
    if limit > 30: limit = 30

    if q:
        result = DocumentTest.find(Text(q))
    else:
        result = DocumentTest.find({})

    if source:
        result = DocumentTest.find({"source": source})

    total = await result.count()
    result = await result.skip(skip).limit(limit).to_list()

    return {"q": q,"db_name": db_name, "source": source, "total": total, "skip": skip, "limit": limit, "db_list": settings.optional_db_list, "data": result}


@router.post("/delete", summary='删除该资料', description="根据_id删除该资料，并同步删除矢量数据库中的同源数据")
async def document_delete(body: DocumentParam):
    await init_db(body.db_name, [DocumentTest])
    result = await DocumentTest.find_one(DocumentTest.id == ObjectId(body.id)).delete()

    return {"deleted_count": result.deleted_count, "raw_result": result.raw_result}


@router.post("/update", summary='修改该资料', description="根据_id和新内容修改该资料，并同步修改矢量数据库中的同源数据（需要先删除原有，再矢量化）")
async def document_update(body: DocumentParam):
    await init_db(body.db_name, [DocumentTest])
    result = await DocumentTest.find_one(DocumentTest.id == ObjectId(body.id)).update({"$set": {DocumentTest.content: body.content}})

    return {"raw_result": result.raw_result}



@router.post("/exclude_words/delete", summary='删除否定词',
            description='获取可选数据库列表，否定词列表，该数据库已录入总数')
async def get(content: str,
                      db_name: Union[str, None] = None):
    return 1

@router.post("/", summary='录入资料',
            description='先存入 mongodb 的 documents 文档集，然后录入矢量数据库')
async def save(content: str,
                      db_name: Union[str, None] = None):
    await init_db(db_name, [Document])

    # result = await result.skip(skip).limit(limit).to_list()

    return 1
