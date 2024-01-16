# for pydantic models，主要是post，put的请求体
from langchain_core.documents import Document
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.config import settings
from enum import Enum


