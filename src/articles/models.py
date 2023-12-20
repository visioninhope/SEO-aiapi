# for db models
import pymongo
from beanie import Document, Indexed
from typing import Optional
from datetime import datetime

class Article(Document):
    keyword: Indexed(str, index_type=pymongo.TEXT)
    type: Optional[str] = None
    source: Optional[str] = None
    create_date: datetime = datetime.now()
    content: str


    class Settings:
        name = "articles"

class ArticleTest(Document):
    keyword: Indexed(str, index_type=pymongo.TEXT)
    type: Optional[str] = None
    source: Optional[str] = None
    create_date: datetime = datetime.now()
    content: str


    class Settings:
        name = "articles_test"