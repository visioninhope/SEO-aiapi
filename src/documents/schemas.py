# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from typing import Union, Optional
from src.config import settings
from src.documents.models import MyDocument


class DocumentListOut(BaseModel):
    q: str | None = None
    db_name: str | None = None
    source: str | None = None
    total: int
    skip: int
    limit: int
    db_list: list[str] = settings.optional_db_list
    data: list[MyDocument]
    negative_keywords: str | None = None


# 用于Document的删除
class DocumentDeleteIn(BaseModel):
    id: str # 变量为_id会无效
    db_name: str | None = None

# 用于Document的修改
class DocumentUpdateIn(BaseModel):
    id: str # 变量为_id会无效
    db_name: str | None = None
    content: Optional[str] = ''

# 用于Document的新建
class DocumentCreateIn(BaseModel):
    db_name: str | None = None
    content: Optional[str] = ''
    source: Optional[str] = ''


class NegativeKeywordsUpdateIn(BaseModel):
    db_name: str | None = None
    value: str | None = ''


# DB 删除，修改，新建结果：{}
class DBResultOut(BaseModel):
    raw_result: dict | str