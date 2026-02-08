from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    mongo_uri: str
    mongo_db: str = "chatbot_db"

    # LINE
    line_channel_secret: str | None = None
    line_channel_token: str | None = None

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
