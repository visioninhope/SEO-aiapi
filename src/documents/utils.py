# non-business logic functions, e.g. response normalization, data enrichment, etc.
import os
import chromadb
from langchain.retrievers import MultiQueryRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_google_genai import GoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from src.adventures.models import Adventure
from src.config import settings
from dotenv import load_dotenv, find_dotenv
from src.documents.schemas import ParserEnum, RetrieverTypeEnum, ModelNameEnum, RagIn
from src.utils import init_db
from datetime import datetime

load_dotenv(find_dotenv(), override=True)


# 从chroma删除source匹配的记录
def delete_from_chroma_by_source(source: str):
    client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
    collection = client.get_collection("langchain")
    collection.delete(where={"source": source})


# 分割文本，并存入chroma，添加source
async def text_splitter_and_save_to_chroma(text: list[str], source: str, chunk_size: int):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size * 0.2)
    documents = text_splitter.create_documents(text, [{"source": source}])
    await Chroma.afrom_documents(documents, OpenAIEmbeddings(),
                                 persist_directory=settings.chroma_persist_directory)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# 简单rag，需要提供topic和system_message_prompt。parser_type即返回值有str和json2种选择，fetch_k为矢量数据库mmr搜索拿到的数据总数，k为返回的数量，MultiQuery模式为最复杂模式，首先生成3个额外查询，然后用mmr搜索到结果，最终用cohere排序
async def rag_topic_to_answer_by_gemini(topic: str,
                                        system_message_prompt: str,
                                        llm_model_name: ModelNameEnum = "gemini-pro",
                                        retriever_type: RetrieverTypeEnum = "mmr",
                                        parser_type: ParserEnum = "str",
                                        fetch_k: int = 10,
                                        k: int = 3):
    retriever = Chroma(embedding_function=OpenAIEmbeddings(),
                       persist_directory=os.environ.get("CHROMA_PERSIST_DIRECTORY")).as_retriever(search_type="mmr",
                                                                                                  search_kwargs={
                                                                                                      "fetch_k": fetch_k,
                                                                                                      "k": k})

    llm_for_multi_query = ChatOpenAI()
    if llm_model_name == ModelNameEnum.gemini_pro:
        llm = GoogleGenerativeAI(model="gemini-pro", max_output_tokens=2048)
    else:
        llm = ChatOpenAI(model_name=llm_model_name, request_timeout=300)

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

# 生成rag内容并保存在mongodb
async def rag_and_save(data: RagIn):
    result = await rag_topic_to_answer_by_gemini(data.topic, data.system_message_prompt, data.llm_model_name,
                                                 data.retriever_type, data.parser_type, data.fetch_k, data.k)

    await init_db(settings.db_name, [Adventure])
    context_dict = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in result["context"]]
    db_data = Adventure(topic=data.topic, answer=result["answer"], context=context_dict,
                        system_message_prompt=data.system_message_prompt, llm_model_name=data.llm_model_name,
                        retriever_type=data.retriever_type, parser_type=data.parser_type, fetch_k=data.fetch_k,
                        k=data.k, create_date=datetime.now())
    await db_data.insert()

    result["system_message_prompt"] = data.system_message_prompt
    result["llm_model_name"] = data.llm_model_name
    result["retriever_type"] = data.retriever_type
    result["parser_type"] = data.parser_type
    result["fetch_k"] = data.fetch_k
    result["k"] = data.k

    return result