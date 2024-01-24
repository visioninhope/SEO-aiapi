from beanie.odm.operators.find.evaluation import Text
from fastapi import APIRouter, BackgroundTasks

from src.documents.schemas import ParserEnum, RetrieverTypeEnum, ModelNameEnum
from src.documents.utils import rag_topic_to_answer
from ..utils import init_db
from typing import Union
from bson.objectid import ObjectId
from .models import Article, ArticleTypeEnum, ArticleOption
from .schemas import ArticleDeleteIn, ArticleCreateIn, ArticleOptionCreateIn, ArticleOptionDeleteIn
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


@router.post("/", summary="生成长文章",  description="根据关键词生成json大纲，然后根据每段大纲生成段落，组合成为长文章")
async def article_create(data: ArticleCreateIn, background_tasks: BackgroundTasks):
    outline_prompt = """You are an expert blogger for researchers who need to know about lab equipment,use the following steps to respond to user inputs. do not output steps, only output results.
Step 1:You will be provided with some contexts related to the topic:"{topic}".
Step 2:Determine the reader’s search intent for the "{topic}", create Attention-Grabbing article titles with energy words around the topic and contexts provided to you.
Step 3:Write a high quality outline as detailed as possible for the topic:"{topic}" referring to the contexts provided to you. The outline should be able to deduce the point of view of the title step by step. The number of headings is between 5 and 10. 
Step 4:Output the outline by JSON object structured like:{{"title": "", "sections": [{{"heading": "", "content":""}}]}}
    """
    outline_json = await rag_topic_to_answer(data.keyword,
                              outline_prompt,
                              data.article_parameter.outline_model,
                              data.article_parameter.outline_retriever_type,
                              ParserEnum.json,
                              data.article_parameter.outline_fetch_k,
                              data.article_parameter.outline_k)
    return outline_json

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