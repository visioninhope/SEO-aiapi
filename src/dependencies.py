# router dependencies
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.config import settings


# 初始化mongodb数据库
async def init_db(db_name: str, models: list):
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    if not db_name: db_name = settings.db_name
    elif db_name not in settings.optional_db_list:
        raise HTTPException(status_code=500, detail="错误的数据库名称")
    await init_beanie(database=client[db_name], document_models=models)
