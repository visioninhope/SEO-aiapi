# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from typing import Union, Optional
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
    raw_result: dict | str

# LLM输出的answer的可选类，获取枚举数据：ParserEnum.__members__.items()
class ParserEnum(str, Enum):
    str = "str"
    json = "json"

class RetrieverTypeEnum(str, Enum):
    mmr = "mmr"
    multi_query = "MultiQuery"
