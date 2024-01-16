# for pydantic models，主要是post，put的请求体
from pydantic import BaseModel
from typing import Optional
from src.config import settings
from enum import Enum


# LLM输出的answer的可选类，获取枚举数据：ParserEnum.__members__.items()
class ParserEnum(str, Enum):
    str = "str"
    json = "json"

class RetrieverTypeEnum(str, Enum):
    mmr = "mmr"
    multi_query = "MultiQuery"
