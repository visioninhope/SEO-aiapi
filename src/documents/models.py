# for db models
import pymongo
from beanie import Document, Indexed
from typing import Optional, Annotated
from datetime import datetime
from typing import Union
from src.config import settings


class Document(Document):
    source: Annotated[str, Indexed(unique=True)]
    create_date: datetime = datetime.now()
    embed: bool = False
    content: Annotated[str, Indexed(index_type=pymongo.TEXT)]

    class Settings:
        name = "documents"

class DocumentTest(Document):
    source: Annotated[str, Indexed(unique=True)]
    create_date: datetime = datetime.now()
    embed: bool = False
    content: Annotated[str, Indexed(index_type=pymongo.TEXT)]

    class Settings:
        name = "documents_test"

class Config(Document):
    key: Annotated[str, Indexed(unique=True)]
    name: Optional[str] = None
    excerpt: Optional[str] = None
    value: Optional[str] = None

    class Settings:
        name = "configs"