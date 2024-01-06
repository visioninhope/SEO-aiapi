# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from typing import Union, Optional
from src.config import settings

# 用于Document的查找，删除，修改
class DocumentParam(BaseModel):
    id: Optional[str] = None # 变量为_id会无效
    db_name: Union[str, None] = settings.db_name
    content: Optional[str] = ''
    source: Optional[str] = ''
