# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from src.articles.models import Article, ArticleParameter
from src.config import settings

# 用于Article的删除的输入值
class ArticleDeleteIn(BaseModel):
    id: str # 变量为_id会无效
    db_name: str | None = None


# 文章批量生成输入参数
class ArticleCreateIn(BaseModel):
    keywords: str # 按行分开的关键词
    article_option_id: str # 文章配置的id


# 文章参数生成
class ArticleOptionCreateIn(BaseModel):
    name: str
    parameter: ArticleParameter
    excerpt: str | None = ""


class ArticleOptionDeleteIn(BaseModel):
    id: str # 变量为_id会无效