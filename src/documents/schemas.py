# for pydantic models，主要是post，put的请求体
from langchain_core.documents import Document
from pydantic import BaseModel
from typing import Union, Optional, Dict, Any
from src.config import settings
from src.documents.models import MyDocument
from enum import Enum


class DocumentListOut(BaseModel):
    q: str | None = None
    db_name: str | None = None
    source: str | None = None
    total: int
    skip: int
    limit: int
    chunk_size: int
    db_list: list[str] = settings.optional_db_list
    data: list[MyDocument]
    negative_keywords: str | None = None


# 用于Document的删除
class DocumentDeleteIn(BaseModel):
    id: str # 变量为_id会无效
    source: str
    db_name: str | None = None

# 用于Document的修改
class DocumentUpdateIn(BaseModel):
    id: str # 变量为_id会无效
    source: str
    chunk_size: int | None = settings.chunk_size
    db_name: str | None = None
    content: Optional[str] = ''

# 用于Document的新建
class DocumentCreateIn(BaseModel):
    chunk_size: int | None = settings.chunk_size
    db_name: str | None = None
    content: Optional[str] = ''
    source: str


class NegativeKeywordsUpdateIn(BaseModel):
    db_name: str | None = None
    value: str | None = ''


# DB 删除，修改，新建结果：{}
class DBResultOut(BaseModel):
    message: str

# LLM输出的answer的可选类，获取枚举数据：ParserEnum.__members__.items()
class ParserEnum(str, Enum):
    str = "str"
    json = "json"

class RetrieverTypeEnum(str, Enum):
    mmr = "mmr"
    multi_query = "MultiQuery"

# 可选的模型
class ModelNameEnum(str, Enum):
    gemini_pro = "gemini-pro"
    gpt_3_5_turbo = "gpt-3.5-turbo"
    gpt_3_5_turbo_16k = "gpt-3.5-turbo-16k"
    gpt_4 = "gpt-4"

# Rag生成输入参数
class RagIn(BaseModel):
    topic: str
    system_message_prompt: str | None
    llm_model_name: ModelNameEnum = ModelNameEnum.gemini_pro
    retriever_type: RetrieverTypeEnum = RetrieverTypeEnum.mmr
    parser_type: ParserEnum = ParserEnum.str
    fetch_k: int = settings.rag_default_fetch_k
    k: int = settings.rag_default_k


# Chat生成输入参数
class ChatIn(BaseModel):
    human_1: str
    llm_model_name: ModelNameEnum = ModelNameEnum.gemini_pro
    temperature: float = 0.7
    system_message_prompt: str | None = ""
    ai_1: str | None = ""
    human_2: str | None = ""

