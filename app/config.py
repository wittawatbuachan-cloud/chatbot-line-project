# app/config.py
from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os



class Settings(BaseSettings):
    mongo_uri: str
    mongo_db: str

    line_channel_secret: str | None = None
    line_channel_token: str | None = None
    llm_api_key: str | None = None

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"   # ⭐ จุดแก้ปัญหานี้
    )

settings = Settings()