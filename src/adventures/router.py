from fastapi import APIRouter

from ..config import settings
from ..documents.schemas import RagIn, ParserEnum, RetrieverTypeEnum
from ..documents.utils import rag_topic_to_answer_by_gemini


router = APIRouter(
    prefix='/adventure',
    tags=['测试各种prompt与参数']
)

@router.get("/rag",  summary='Rag测试列表页', description="")
async def rag_list():
    return {"db_name": settings.db_name, "fetch_k": settings.rag_default_fetch_k, "k": settings.rag_default_k, "retriever_types": RetrieverTypeEnum.__members__.items(), "parser_types": ParserEnum.__members__.items()}

@router.post("/rag", summary='Rag1问1答测试提交', description="system_message_prompt 中用 {topic} 代替话题存在的位置，第一句一般是：You will be provided with some contexts delimited by triple quotes. 这样就可以把context作为第一波用户输入自然而然的生成结果")
async def rag_post(data: RagIn):
    result = await rag_topic_to_answer_by_gemini(data.topic, data.system_message_prompt, data.retriever_type, data.parser_type, data.fetch_k, data.k)

    return result
