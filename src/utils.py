import os
import random

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.config import settings
import requests
import json
from bs4 import BeautifulSoup

# 初始化mongodb数据库
async def init_db(db_name: str, models: list):
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    if not db_name:
        db_name = settings.db_name
    elif db_name not in settings.optional_db_list:
        raise HTTPException(status_code=500, detail="错误的数据库名称")
    await init_beanie(database=client[db_name], document_models=models)


# 使用zhile的deeplx服务来翻译：https://fakeopen.org/DeepLX
def trans_by_deepl(text: str, source_lang: str = "EN", target_lang: str = "ES"):
    payload = json.dumps({
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    })
    headers = {
        'Content-Type': 'application/json'
    }

    tries = 10
    response = None
    for i in range(tries):
        # url = random.choice(settings.deeplx_base_urls)
        url = "https://api.deeplx.org/translate"
        try:
            response = requests.request("POST",url , headers=headers, data=payload, timeout=3)
            if json.loads(response.text)['code'] == 200:
                print("翻译成功 - " + url)
                break
            else:
                if i < tries - 1:
                    print("翻译失败，重试中 - " + url)
                    continue
                else:
                    break
        except:
            print("响应失败，重试中 - " + url)

    return json.loads(response.text)['data']


# 可以翻译html，把每段文本提取出来分别翻译
def trans(text, source_lang: str = "EN", target_lang: str = "ES"):
    soup = BeautifulSoup(text, "html.parser")
    for element in soup.find_all(string=True):
        if not element.isspace():
            translated_text = trans_by_deepl(element, source_lang, target_lang)
            element.replace_with(translated_text)

    for img in soup.find_all('img'):
        if not img['alt'].isspace():
            translated_text = trans_by_deepl(img['alt'], source_lang, target_lang)
            img['alt'] = translated_text

    return soup