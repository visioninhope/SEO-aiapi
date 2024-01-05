# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from typing import Union
from src.config import settings

# 用于Article的查找，删除，修改
class ArticleParam(BaseModel):
    id: str # 变量为_id会无效
    db_name: Union[str, None] = settings.db_name
