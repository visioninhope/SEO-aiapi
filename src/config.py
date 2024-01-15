from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))

class Settings(BaseSettings):
    openai_api_key: str | None
    cohere_api_key: str | None
    # 允许访问的IP列表
    allowed_ips: list
    deeplx_base_urls: list
    google_trans_api_key: str
    db_name: str
    optional_db_list: list
    chroma_persist_directory : str
    chunk_size: int
    chunk_overlap: int

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()