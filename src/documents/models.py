# for db models
import pymongo
from beanie import Document, Indexed
from typing import Optional, Annotated
from datetime import datetime
from src.config import settings


class MyDocument(Document):
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


class RagPromptLog(Document):
    system_prompt: str
    topic: str
    answer: str
    context: Optional[str] = ''

class Config(Document):
    key: Annotated[str, Indexed(unique=True)]
    value: Optional[str] = ''
    name: Optional[str] = ''
    excerpt: Optional[str] = ''

    class Settings:
        name = "configs"