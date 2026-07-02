import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./melomecate.db"
    FERNET_KEY: str = "E9p4eS09Wj3i1b4X8y5pQ7c3L5U8K6s3d1L8H9u2z3M="
    GEMINI_API_KEY: Optional[str] = None
    WHATSAPP_TOKEN: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: str = "my_secure_verify_token_123"
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
