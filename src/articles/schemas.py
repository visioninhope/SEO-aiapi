# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from src.articles.models import Article, ArticleParameter
from src.config import settings

# 用于Article的删除的输入值
class ArticleDeleteIn(BaseModel):
    id: str # 变量为_id会无效
    db_name: str | None = None

class ArticleCreateIn(BaseModel):
    keyword: str
    article_parameter: ArticleParameter


class ArticleOptionCreateIn(BaseModel):
    name: str
    parameter: ArticleParameter
    excerpt: str | None = ""


class ArticleOptionDeleteIn(BaseModel):
    id: str # 变量为_id会无效