from beanie.odm.operators.find.evaluation import Text
from fastapi import APIRouter, BackgroundTasks

from src.documents.schemas import RetrieverTypeEnum, ModelNameEnum
from .service import article_create_one
from ..utils import init_db
from typing import Union
from bson.objectid import ObjectId
from .models import Article, ArticleTypeEnum, ArticleOption, ArticleParameter
from .schemas import ArticleDeleteIn, ArticleCreateIn, ArticleOptionCreateIn, ArticleOptionDeleteIn
from src.config import settings

router = APIRouter(
    prefix='/article',
    tags=['文章']
)


@router.get("",
            summary='获取文章',
            description='根据关键词从数据库获取文章，参数列表：q, type, skip, limit, db_name。可选type为：mixed_rewrite, rewrite, original')
async def article_get(q: Union[str, None] = None,
                      skip: int = 0,
                      limit: int = 10,
                      type: Union[str, None] = None):
    await init_db(settings.db_name, [Article, ArticleOption])

    if limit > 30: limit = 30
    result = Article.find(Text(q)) if q else Article.find({})
    if type: result = result.find({"type": type})

    total = await result.count()
    result = await result.sort(-Article.create_date).skip(skip).limit(limit).to_list()
    article_options = await ArticleOption.find_all().to_list()

    return {"q": q, "db_name": settings.db_name, "type": type, "types": ArticleTypeEnum.__members__.items(), "total": total, "skip": skip, "limit": limit, "article_options": article_options, "data": result}


@router.post("", summary="批量生成长文章",  description="根据关键词生成json大纲，然后根据每段大纲生成段落，组合成为长文章")
async def articles_create(data: ArticleCreateIn, background_tasks: BackgroundTasks):
    await init_db(settings.db_name, [ArticleOption])
    article_option = await ArticleOption.find_one(ArticleOption.id == ObjectId(data.article_option_id))
    for keyword in data.keywords.splitlines():
        background_tasks.add_task(article_create_one, keyword, article_option.parameter)

    return {"message": "The article has started to be generated, please wait for a while and refresh the page."}


@router.post("/delete", summary='删除文章', description="根据_id删除数据集articles中的文章")
async def article_delete(data: ArticleDeleteIn):
    await init_db(settings.db_name, [Article])
    result = await Article.find_one(Article.id == ObjectId(data.id)).delete()

    return {"raw_result": result.raw_result}


@router.get("/option", summary="获取文章prompt配置，包括大纲，文本")
async def option_get():
    await init_db(settings.db_name, [ArticleOption])
    result = await ArticleOption.find_all().sort(-ArticleOption.create_date).to_list()

    return {"data": result, "retriever_types":  RetrieverTypeEnum.__members__.items(), "llm_model_names": ModelNameEnum.__members__.items()}


@router.post("/option", summary="创建文章prompt配置，包括大纲，文本，可以配合人设搞多组配置")
async def option_create(data: ArticleOptionCreateIn):
    await init_db(settings.db_name, [ArticleOption])
    article_option = ArticleOption(name=data.name, parameter=data.parameter, excerpt=data.excerpt)
    try:
        await article_option.insert()
    except Exception as e:
        return {"message": 'xxx ' + str(e) + ' xxx'}
    return {"message": "article option create success!"}


@router.post("/option/delete", summary='删除文章配置', description="根据_id删除该文章配置")
async def document_delete(body: ArticleOptionDeleteIn):
    await init_db(settings.db_name, [ArticleOption])
    await ArticleOption.find_one(ArticleOption.id == ObjectId(body.id)).delete()

    return {"message": "article option delete success!"}