# module specific business logic
import logging
import traceback
from datetime import datetime

from src.adventures.models import AdventureRag, AdventureChat
from src.config import settings
from src.documents.schemas import RagIn, ChatIn
from src.documents.utils import rag_topic_to_answer, chat_to_answer
from src.utils import init_db


# 生成rag内容并保存在mongodb
async def rag_and_save(data: RagIn, tries: int = 6):
    for i in range(tries):
        try:
            result = await rag_topic_to_answer(data.topic, data.system_message_prompt, data.llm_model_name,
                                               data.retriever_type, data.parser_type, data.fetch_k, data.k)

            await init_db(settings.db_name, [AdventureRag])
            context_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in result["context"]]
            db_data = AdventureRag(topic=data.topic, answer=result["answer"], context=context_dict,
                                   system_message_prompt=data.system_message_prompt, llm_model_name=data.llm_model_name,
                                   retriever_type=data.retriever_type, parser_type=data.parser_type, fetch_k=data.fetch_k,
                                   k=data.k, create_date=datetime.now())
            await db_data.insert()
            return result
        except Exception as e:
            logging.error(str(e))
            traceback.print_exc(file=open(settings.log_file, "a"))
            if i == tries - 1:
                logging.error("Rag generation failed - " + data.topic)


# 生成常规chat测试并存储到数据库
async def chat_and_save(chat_in_data: ChatIn, tries: int = 6):
    for i in range(tries):
        try:
            answer = await chat_to_answer(chat_in_data.human_1, chat_in_data.llm_model_name, chat_in_data.temperature,chat_in_data.system_message_prompt, chat_in_data.ai_1, chat_in_data.human_2)

            await init_db(settings.db_name, [AdventureChat])
            db_data = AdventureChat(system_message_prompt=chat_in_data.system_message_prompt,
                                    human_1=chat_in_data.human_1,
                                    ai_1=chat_in_data.ai_1,
                                    human_2=chat_in_data.human_2, answer=answer,
                                    llm_model_name=chat_in_data.llm_model_name,
                                    temperature=chat_in_data.temperature, create_date=datetime.now())
            await db_data.insert()
            return True
        except Exception as e:
            logging.error(str(e))
            traceback.print_exc(file=open(settings.log_file, "a"))
            if i == tries - 1:
                logging.error("Chat generation failed - " + chat_in_data.human_1)