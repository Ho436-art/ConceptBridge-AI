"""
Configuration Helper Module
"""

import os
from dotenv import load_dotenv

def load_config() -> dict:
    """Load application configuration from environment variables."""
    load_dotenv()
    return {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "GROQ_MODEL": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "GROQ_STT_MODEL": os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "APP_ENV": os.getenv("APP_ENV", "development"),
        "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///database/conceptbridge.db"),
        "DB_FILE_PATH": os.getenv("DB_FILE_PATH", "database/conceptbridge.db"),
        "SMART_REFRESH_MAX_DURATION_SECONDS": int(os.getenv("SMART_REFRESH_MAX_DURATION_SECONDS", "300")),
        "SMART_REFRESH_COOLDOWN_MINUTES": int(os.getenv("SMART_REFRESH_COOLDOWN_MINUTES", "30"))
    }
