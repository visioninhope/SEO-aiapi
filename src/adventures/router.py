from fastapi import APIRouter, BackgroundTasks
from pymongo import MongoClient

from .models import Adventure
from ..config import settings
from ..documents.schemas import RagIn, ParserEnum, RetrieverTypeEnum, ModelNameEnum
from ..documents.utils import rag_topic_to_answer_by_gemini, rag_and_save
from ..utils import init_db

router = APIRouter(
    prefix='/adventure',
    tags=['测试各种prompt与参数']
)


@router.get("/rag", summary='Rag测试列表页', description="")
async def rag_list(skip: int = 0,
                   limit: int = 10, ):
    await init_db(settings.db_name, [Adventure])
    result = Adventure.find_all()
    result = await result.sort(-Adventure.create_date).skip(skip).limit(limit).to_list()
    # 用最新记录的值来填写生成用的默认值
    last_result = await Adventure.find({}).sort(-Adventure.create_date).first_or_none()
    if last_result:
        fetch_k = last_result.fetch_k
        k = last_result.k
        llm_model_name = last_result.llm_model_name
        retriever_type = last_result.retriever_type
        parser_type = last_result.parser_type
        system_message_prompt = last_result.system_message_prompt
    else:
        fetch_k = settings.rag_default_fetch_k
        k = settings.rag_default_k
        llm_model_name = None
        retriever_type = None
        parser_type = None
        system_message_prompt = None

    return {"db_name": settings.db_name, "fetch_k": fetch_k, "k": k, "llm_model_name": llm_model_name,
            "retriever_type": retriever_type, "parser_type": parser_type,
            "system_message_prompt": system_message_prompt,
            "llm_model_names": ModelNameEnum.__members__.items(),
            "retriever_types": RetrieverTypeEnum.__members__.items(), "parser_types": ParserEnum.__members__.items(),
            "skip": skip, "limit": limit,
            "data": result}


@router.post("/rag", summary='Rag1问1答测试提交(后台运行)',
             description="system_message_prompt 中用 {topic} 代替话题存在的位置，第一句一般是：You will be provided with some contexts delimited by triple quotes. 这样就可以把context作为第一波用户输入自然而然的生成结果。MultiQuery搜索流程：首先chatgpt生成3个相似问题，然后chroma中用mmr方法查询原问题+3个相似问题，得出结果用cohere排序，最终用gemini-pro生成(为了降低成本)")
async def rag_post(data: RagIn, background_tasks: BackgroundTasks):
    background_tasks.add_task(rag_and_save, data)
    return {"message": "Task has been added to the queue."}
