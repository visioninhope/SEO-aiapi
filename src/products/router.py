from fastapi import APIRouter
from src.config import settings
from ..utils import init_db

router = APIRouter(
    prefix='/product',
    tags=['产品与产品分类']
)


@router.get("", summary="产品生成与列表页面")
async def product_list():
    return {"message": "Hello World"}