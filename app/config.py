from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    mongo_db: str = "chatbot_db"

    class Config:
        env_prefix = ""   # สำคัญ
        case_sensitive = False

settings = Settings()
