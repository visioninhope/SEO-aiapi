from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    openai_key: str | None
    items_per_user: int = 50

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
print(settings.openai_key)