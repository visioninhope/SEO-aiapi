# for db models
from beanie import Document, Indexed
from typing import Optional, Annotated
from datetime import datetime
from src.config import settings


class Config(Document):
    key: Annotated[str, Indexed(unique=True)]
    value: Optional[str] = ''
    name: Optional[str] = ''
    excerpt: Optional[str] = ''

    class Settings:
        name = "configs"