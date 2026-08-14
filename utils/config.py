"""
Configuration Helper Module
"""

import os
from dotenv import load_dotenv

def load_config() -> dict:
    """Load application configuration from environment variables."""
    load_dotenv()
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "APP_ENV": os.getenv("APP_ENV", "development"),
        "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///database/conceptbridge.db"),
        "DB_FILE_PATH": os.getenv("DB_FILE_PATH", "database/conceptbridge.db"),
        "SMART_REFRESH_MAX_DURATION_SECONDS": int(os.getenv("SMART_REFRESH_MAX_DURATION_SECONDS", "300"))
    }
