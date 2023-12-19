# router dependencies
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie


# 初始化mongodb数据库
async def init_db(db_name: str, models: list):
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client[db_name], document_models=models)
