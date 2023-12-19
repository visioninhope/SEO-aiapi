# for db models
import pymongo
from beanie import Document, Indexed


class Article(Document):
    keyword: Indexed(str, index_type=pymongo.TEXT)
    content: str

    class Settings:
        name = "articles"
