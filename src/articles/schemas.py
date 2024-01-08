# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from src.articles.models import Article
from src.config import settings

# Article列表页的返回值
class ArticleListOut(BaseModel):
    q: str | None = None
    db_name: str | None = None
    type: str | None = None
    total: int
    skip: int
    limit: int
    db_list: list[str] = settings.optional_db_list
    data: list[Article]

# 用于Article的删除的输入值
class ArticleDeleteIn(BaseModel):
    id: str # 变量为_id会无效
    db_name: str | None = None

# 删除Article的返回值
class ArticleDeleteOut(BaseModel):
    raw_result: dict | str