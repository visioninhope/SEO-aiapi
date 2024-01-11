# non-business logic functions, e.g. response normalization, data enrichment, etc.
import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src.config import settings

# 从chroma删除source匹配的记录
def delete_from_chroma_by_source(source: str):
    client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
    collection = client.get_collection("langchain")
    collection.delete(where={"source": source})


# 分割文本，并存入chroma，添加source
async def text_splitter_and_save_to_chroma(text: list[str], source: str, chunk_size: int):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_size*0.2)
    documents = text_splitter.create_documents(text, [{"source": source}])
    await Chroma.afrom_documents(documents, OpenAIEmbeddings(),
                                 persist_directory=settings.chroma_persist_directory)