# for db models
from beanie import Document, Indexed
from typing import Optional
from datetime import datetime
from src.config import settings

# 存放每次进行prompt测试的结果
class AdventureRag(Document):
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
        name = "adventures_rag"

class AdventureChat(Document):
    system_message_prompt: Optional[str] = ''
    human_1: str
    ai_1: Optional[str] = ''
    human_2: Optional[str] = ''
    answer: str | dict
    llm_model_name: str
    temperature: float = 0.7
    create_date: Optional[datetime] = datetime.now()

    class Settings:
        name = "adventures_chat"