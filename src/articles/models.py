# for db models
from enum import Enum

import pymongo
from beanie import Document, Indexed
from typing import Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field
from src.config import settings
from src.documents.schemas import RetrieverTypeEnum, ModelNameEnum

class ArticleParameter(BaseModel):
    outline_prompt: str = Field(max_length=2000)
    outline_model: ModelNameEnum = ModelNameEnum.gemini_pro
    outline_retriever_type: RetrieverTypeEnum = RetrieverTypeEnum.mmr
    outline_fetch_k: int = Field(default=settings.rag_default_fetch_k, gt=0, le=100, description="must 0-100")
    outline_k: int = Field(default=settings.rag_default_k, gt=0, le=100, description="must 0-100")

    paragraph_prompt: str = Field(max_length=2000)
    paragraph_model: ModelNameEnum = ModelNameEnum.gemini_pro
    paragraph_retriever_type: RetrieverTypeEnum = RetrieverTypeEnum.mmr
    paragraph_fetch_k: int = Field(default=settings.rag_default_fetch_k, gt=0, le=100, description="must 0-100")
    paragraph_k: int = Field(default=settings.rag_default_k, gt=0, le=100, description="must 0-100")


class ArticleTypeEnum(str, Enum):
    original = "original"
    mixed_rewrite = "mixed_rewrite"
    rewrite = "rewrite"


class Article(Document):
    keyword: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    type: Optional[ArticleTypeEnum] = None
    article_option_name: Optional[str] = None
    create_date: datetime = datetime.now()
    article_parameter: Optional[ArticleParameter] = None
    outline: dict | None = None
    content: str
    outline_context: list[dict] | None = None
    paragraph_context: list[dict] | None = None

    class Settings:
        name = "articles"

class ArticleOption(Document):
    name: Annotated[str, Indexed(unique=True)]
    parameter: ArticleParameter
    excerpt: str | None = ""
    create_date: Optional[datetime] = datetime.now()

    class Settings:
        name = "article_options"