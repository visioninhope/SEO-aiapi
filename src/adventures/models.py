# for db models
from beanie import Document, Indexed
from typing import Optional
from datetime import datetime
from src.config import settings

# 存放每次进行prompt测试的结果
class Adventure(Document):
    topic: str
    answer: str | dict
    llm_model_name: str
    retriever_type: str
    parser_type: str
    fetch_k: int
    k: int
    system_message_prompt: str
    context: list[dict]
    create_date: Optional[datetime] = datetime.now()

    class Settings:
        name = "adventures"