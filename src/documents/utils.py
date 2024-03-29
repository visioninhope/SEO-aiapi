# non-business logic functions, e.g. response normalization, data enrichment, etc.
import os
import traceback

import chromadb
from langchain.retrievers import MultiQueryRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import LongContextReorder
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_google_genai import GoogleGenerativeAI
from langchain_openai import ChatOpenAI, AzureOpenAIEmbeddings
from src.adventures.models import AdventureRag, AdventureChat
from src.config import settings
from dotenv import load_dotenv, find_dotenv
from src.documents.schemas import ParserEnum, RetrieverTypeEnum, ModelNameEnum, RagIn, ChatIn
from src.utils import init_db
from datetime import datetime
import logging

logging.basicConfig(filename=settings.log_file, format='%(asctime)s: %(levelname)s - %(message)s')
load_dotenv(find_dotenv(), override=True)


# 从chroma删除source匹配的记录
def delete_from_chroma_by_source(source: str):
    client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
    collection = client.get_or_create_collection("langchain")
    collection.delete(where={"source": source})


# 尝试给出一个更好的chunk_size，先用给的chunk_size切割，如果有段落小于100或段落太长，说明大小不太合适，就加点
def better_chunk_size(text: str, chunk_size: int):
    new_chunk_size = chunk_size
    for i in range(5):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=new_chunk_size,
            chunk_overlap=new_chunk_size * 0.2,
        )
        for p in text_splitter.split_text(text):
            if len(p) < 80:
                new_chunk_size += 80
                break
            if len(p) > new_chunk_size - 10:
                new_chunk_size += 200
                break
    return new_chunk_size


# 分割文本，并存入chroma，添加source
async def text_splitter_and_save_to_chroma(text: list[str], source: str, chunk_size: int):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size * 0.2,
                                                   add_start_index=True)
    documents = text_splitter.create_documents(text, [{"source": source}])
    embedding = AzureOpenAIEmbeddings(azure_endpoint=settings.ai_azure_endpoint,
                                      openai_api_key=settings.ai_azure_openai_api_key,
                                      deployment=settings.ai_azure_deployment_embed)
    await Chroma.afrom_documents(documents, embedding, persist_directory=settings.chroma_persist_directory)
    return documents


# 移除重复文档（用于多次查询后合并的文档）
def get_unique_docs(docs):
    seen = set()
    unique_docs = []
    for obj in docs:
        unique_value = obj.metadata["source"] + str(obj.metadata["start_index"])
        if unique_value not in seen:
            seen.add(unique_value)
            unique_docs.append(obj)
    return unique_docs


# 将文档合并为一段context，如果超过3个文档，就重排下顺序，根据论文：https://arxiv.org/abs/2307.03172
def format_docs(docs):
    if len(docs) > 3:
        reordering = LongContextReorder()
        docs = reordering.transform_documents(docs)
    return "\n\n".join(doc.page_content for doc in docs)


# 简单rag，需要提供topic和system_message_prompt。parser_type即返回值有str和json2种选择，fetch_k为矢量数据库mmr搜索拿到的数据总数，k为返回的数量，MultiQuery模式为最复杂模式，首先生成3个额外查询，然后用mmr搜索到结果，最终用cohere排序
async def rag_topic_to_answer(topic: str,
                              system_message_prompt: str,
                              llm_model_name: ModelNameEnum = "gemini-pro",
                              retriever_type: RetrieverTypeEnum = "mmr",
                              parser_type: ParserEnum = "str",
                              fetch_k: int = 10,
                              k: int = 3):
    embedding = AzureOpenAIEmbeddings(azure_endpoint=settings.ai_azure_endpoint,
                                      openai_api_key=settings.ai_azure_openai_api_key,
                                      deployment=settings.ai_azure_deployment_embed)

    retriever = Chroma(embedding_function=embedding,
                       persist_directory=os.environ.get("CHROMA_PERSIST_DIRECTORY")).as_retriever(search_type="mmr",
                                                                                                  search_kwargs={
                                                                                                      "fetch_k": fetch_k,
                                                                                                      "k": k})

    llm_for_multi_query = ChatOpenAI(openai_api_key=settings.ai_openai_api_key)
    if llm_model_name == ModelNameEnum.gemini_pro:
        llm = GoogleGenerativeAI(model="gemini-pro", max_output_tokens=2048)
    else:
        llm = ChatOpenAI(model_name=llm_model_name, request_timeout=300,
                         openai_api_key=settings.ai_transit_openai_api_key,
                         openai_api_base=settings.ai_transit_openai_api_base)

    if retriever_type == RetrieverTypeEnum.multi_query:
        retriever = MultiQueryRetriever.from_llm(
            retriever=retriever, llm=llm_for_multi_query
        )
        compressor = CohereRerank(top_n=k)
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )

    chat_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_message_prompt),
            ("human", "{context}"),
        ],
    )

    parser = StrOutputParser()
    if parser_type == "json": parser = JsonOutputParser()
    rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
            | chat_template
            | llm
            | parser
    )
    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "topic": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)

    result = ""
    tries = 3
    for i in range(tries):
        try:
            result = await rag_chain_with_source.ainvoke(topic)
        except OutputParserException:
            if i < tries - 1:
                print("输出格式不为json，重试中...")
                continue
            else:
                raise
        break

    return result


# 常规chat对话
async def chat_to_answer(human_1: str,
                         llm_model_name: ModelNameEnum = ModelNameEnum.gemini_pro,
                         temperature: float = 0.7,
                         system_message_prompt: str | None = "",
                         ai_1: str | None = "",
                         human_2: str | None = ""):
    full_messages = [
        ("system", system_message_prompt),
        ("human", human_1),
        ("ai", ai_1),
        ("human", "{user_input}"),
    ]
    # 模型切换
    if llm_model_name == ModelNameEnum.gemini_pro:
        llm = GoogleGenerativeAI(model="gemini-pro", max_output_tokens=2048)
        # gemini模型没有system prompt，2轮对话分割点也得变
        full_messages.pop(0)
    else:
        llm = ChatOpenAI(model_name=llm_model_name, request_timeout=300, temperature=temperature,
                         openai_api_key=settings.ai_transit_openai_api_key,
                         openai_api_base=settings.ai_transit_openai_api_base)

    # 有ai_1就是2轮对话，1轮与2轮间切换
    if ai_1:
        chat_template = ChatPromptTemplate.from_messages(
            full_messages
        )
        user_input = human_2
    else:
        chat_template = ChatPromptTemplate.from_messages(
            full_messages[-1]
        )
        user_input = human_1

    output_parser = StrOutputParser()
    chain = (
            {"user_input": RunnablePassthrough()}
            | chat_template
            | llm
            | output_parser
    )

    result = await chain.ainvoke(user_input)
    return result