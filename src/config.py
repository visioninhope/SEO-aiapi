from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))

class Settings(BaseSettings):
    openai_key: str | None
    # 允许访问的IP列表
    allowed_ips: list
    db_name: str
    optional_db_list: list

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()