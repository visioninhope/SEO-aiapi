# for db models
import pymongo
from beanie import Document, Indexed
from typing import Optional, Annotated
from datetime import datetime
from src.config import settings


class Article(Document):
    keyword: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    type: Optional[str] = None
    create_date: datetime = datetime.now()
    content: str

    class Settings:
        name = "articles"