# backend/config.py
from proto import Field
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Synchronous database URL for psycopg2 (no +asyncpg prefix)
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    LANGCHAIN_PG_URL: str = os.getenv("LANGCHAIN_PG_URL")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    gmail_sender_address: str = os.getenv("GMAIL_SENDER_ADDRESS")
    gmail_sender_password: str = os.getenv("GMAIL_SENDER_PASSWORD")
    GOOGLE_FORM_LINK: str = os.getenv("GOOGLE_FORM_LINK")
    SHEET_ID: str = os.getenv("SHEET_ID")

    class Config:
        env_file = ".env"

settings = Settings()
