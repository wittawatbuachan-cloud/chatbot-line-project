# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    mongo_db: str = "chatbot_db"

    line_channel_secret: str
    line_channel_token: str

    class Config:
        env_prefix = ""
        case_sensitive = False   # 👈 สำคัญ

settings = Settings()
