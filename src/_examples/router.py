from fastapi import APIRouter
from src.config import settings
from ..utils import init_db

router = APIRouter(
    prefix='/example',
    tags=['文档与数据库']
)

