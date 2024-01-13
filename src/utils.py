from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.config import settings
import requests
import json


# 初始化mongodb数据库
async def init_db(db_name: str, models: list):
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    if not db_name:
        db_name = settings.db_name
    elif db_name not in settings.optional_db_list:
        raise HTTPException(status_code=500, detail="错误的数据库名称")
    await init_beanie(database=client[db_name], document_models=models)


def trans(text: str, source_lang: str = "EN", target_lang: str = "ES"):
    payload = json.dumps({
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    })
    headers = {
        'Content-Type': 'application/json'
    }
    url = "https://api.deeplx.org/translate"

    tries = 3
    response = None
    for i in range(tries):
        response = requests.request("POST", url, headers=headers, data=payload)
        if json.loads(response.text)['code'] == 200:
            break
        else:
            if i < tries - 1:
                print("翻译失败，重试中")
                continue
            else:
                break

    return json.loads(response.text)['data']
