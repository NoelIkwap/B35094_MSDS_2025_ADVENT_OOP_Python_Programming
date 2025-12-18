# config.py - SQLite configuration for Refugee Verification System

from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "refugees.db"

class Settings(BaseSettings):
    # Database Configuration
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Security
    SECRET_KEY: str = "*******************"

    # API Settings (optional)
    API_TITLE: str = "Refugee Verification Portal"
    API_DESCRIPTION: str = "Secure API for verifying refugee identities"
    API_VERSION: str = "1.0.0"
    API_KEY: str = "nsaf-secure-api-key-2025"

    class Config:
        env_file = ".env"

settings = Settings()
