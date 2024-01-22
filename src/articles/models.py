# for db models
from enum import Enum

import pymongo
from beanie import Document, Indexed
from typing import Optional, Annotated
from datetime import datetime
from pydantic import BaseModel
from src.config import settings
from src.documents.schemas import ModelNameEnum, RetrieverTypeEnum


class ArticleParameter(BaseModel):
    outline_prompt: str
    outline_model: ModelNameEnum = ModelNameEnum.gemini_pro
    outline_retriever_type: RetrieverTypeEnum = RetrieverTypeEnum.mmr
    outline_fetch_k: int = settings.rag_default_fetch_k
    outline_k: int = settings.rag_default_k

    paragraph_prompt: str
    paragraph_model: ModelNameEnum = ModelNameEnum.gemini_pro
    paragraph_retriever_type: RetrieverTypeEnum = RetrieverTypeEnum.mmr
    paragraph_fetch_k: int = settings.rag_default_fetch_k
    paragraph_k: int = settings.rag_default_k


class ArticleTypeEnum(str, Enum):
    original = "original"
    mixed_rewrite = "mixed_rewrite"
    rewrite = "rewrite"


class Article(Document):
    keyword: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    type: Optional[ArticleTypeEnum] = None
    create_date: datetime = datetime.now()
    article_parameter: Optional[ArticleParameter] = None
    content: str
    outline_context: str | None = None
    paragraph_context: str | None = None

    class Settings:
        name = "articles"