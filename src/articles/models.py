# for db models
from enum import Enum

import pymongo
from beanie import Document, Indexed
from typing import Optional, Annotated
from datetime import datetime
from src.config import settings


class Article_Parameter(Document):

    outline_prompt: Optional[str] = None
    paragraph_prompt: Optional[str] = None


class ArticleTypeEnum(str, Enum):
    original = "original"
    mixed_rewrite = "mixed_rewrite"
    rewrite = "rewrite"


class Article(Document):
    keyword: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    type: Optional[ArticleTypeEnum] = None
    create_date: datetime = datetime.now()
    content: str
    article_parameter: Optional[Article_Parameter] = None


    class Settings:
        name = "articles"