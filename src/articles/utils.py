# non-business logic functions, e.g. response normalization, data enrichment, etc.
from pymongo import MongoClient
import datetime
import json

# 整mongodb文章，大纲搬家的事
def move_mongodb():
    client = MongoClient()
    db_ai = client["ai"]
    collection_ai_articles = db_ai["chroma_outlines_3"]

    db_kintek = client["kintek"]
    collection_kintek_articles = db_kintek["outlines"]
    collection_kintek_articles.create_index([("keyword", "text")])
    today = datetime.date.today()

    # 记得建立个articles的副本用于删除测试
    for item in collection_ai_articles.find():
        new_item = {}
        new_item["keyword"] = item['keyword']
        new_item["content"] = item["outline"]
        new_item["create_date"] = datetime.datetime.combine(today, datetime.time.min)
        new_item["type"] = "original"

        collection_kintek_articles.insert_one(new_item)
        print(new_item["keyword"] + ' - 插入成功')

def main():
    move_mongodb()

if __name__ == "__main__":
    main()