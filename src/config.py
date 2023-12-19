from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))

class Settings(BaseSettings):
    openai_key: str | None

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()