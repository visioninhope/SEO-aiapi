# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from typing import Union, Optional
from src.config import settings
from src.documents.models import Document


class DocumentListOut(BaseModel):
    q: str | None = None
    db_name: str | None = settings.db_name
    source: str | None = None
    total: int
    skip: int
    limit: int
    db_list: list[str] = settings.optional_db_list
    data: list[Document]


# 用于Document的删除
class DocumentDeleteIn(BaseModel):
    id: str | None = None # 变量为_id会无效
    db_name: str | None = settings.db_name

# 用于Document的修改
class DocumentUpdateIn(BaseModel):
    id: str | None = None # 变量为_id会无效
    db_name: str | None = settings.db_name
    content: Optional[str] = ''

# 用于Document的新建
class DocumentCreateIn(BaseModel):
    db_name: str | None = settings.db_name
    content: Optional[str] = ''
    source: Optional[str] = ''

# Document 删除，修改，新建结果：{}
class DocumentResultOut(BaseModel):
    raw_result: dict | str