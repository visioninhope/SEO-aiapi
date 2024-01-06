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
    content: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    embed: bool = False

    class Settings:
        name = "documents"

class DocumentTest(Document):
    source: Annotated[str, Indexed(unique=True)]
    create_date: datetime = datetime.now()
    content: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    embed: bool = False

    class Settings:
        name = "documents_test"

class Config(Document):
    key: Annotated[str, Indexed(unique=True)]
    name: Optional[str] = None
    excerpt: Optional[str] = None
    value: Optional[str] = None

    class Settings:
        name = "configs"