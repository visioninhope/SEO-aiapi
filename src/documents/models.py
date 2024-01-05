# for db models
import pymongo
from beanie import Document, Indexed
from typing import Optional
from datetime import datetime
from typing import Union
from src.config import settings


class Document(Document):
    source: Optional[str] = None
    create_date: datetime = datetime.now()
    content: str
    embed: bool = False

    class Settings:
        name = "documents"
