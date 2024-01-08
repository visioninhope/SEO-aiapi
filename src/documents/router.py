from datetime import datetime
from beanie.odm.operators.find.evaluation import Text
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter
from src.config import settings
from ..dependencies import init_db
from typing import Union
from bson.objectid import ObjectId
from .models import MyDocument, DocumentTest, Config
from .schemas import DocumentListOut, DocumentDeleteIn, DocumentUpdateIn, DocumentCreateIn, DBResultOut, \
    NegativeKeywordsUpdateIn

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

    return {"q": q,"db_name": db_name, "source": source, "total": total, "skip": skip, "limit": limit, "data": result, "negative_keywords": negative_keywords.value}


@router.post("/delete", response_model=DBResultOut, summary='删除该资料', description="根据_id删除该资料，并同步删除矢量数据库中的同源数据")
async def document_delete(body: DocumentDeleteIn):
    await init_db(body.db_name, [DocumentTest])
    result = await DocumentTest.find_one(DocumentTest.id == ObjectId(body.id)).delete()

    return {"raw_result": result.raw_result}


@router.post("/update", response_model=DBResultOut, summary='修改该资料', description="根据_id和新内容修改该资料，并同步修改矢量数据库中的同源数据（需要先删除原有，再矢量化）")
async def document_update(body: DocumentUpdateIn):
    await init_db(body.db_name, [DocumentTest])
    result = await DocumentTest.find_one(DocumentTest.id == ObjectId(body.id)).update({"$set": {DocumentTest.content: body.content}})

    return {"raw_result": result.raw_result}


@router.post("/create", response_model=DBResultOut, summary='新建资料', description="根据新内容新建资料，并存入矢量数据库")
async def document_update(body: DocumentCreateIn):
    await init_db(body.db_name, [DocumentTest])
    document = DocumentTest(source=body.source, embed=False, create_date=datetime.now(), content=body.content)
    await document.create()

    return {"raw_result": {"n": 1, "ok": 1}}


@router.post("/negative_keywords/update", response_model=DBResultOut, summary='修改否定关键词',
            description='修改configs数据集中 key 为 negative_keywords 的文档')
async def negative_keywords_update(body: NegativeKeywordsUpdateIn):
    await init_db(body.db_name, [Config])
    result = await Config.find_one(Config.key == 'negative_keywords').upsert(
        Set({Config.value: body.value}),
        on_insert=Config(key="negative_keywords", value=body.value))

    return {"raw_result": {"n": 1, "ok": 1}}

