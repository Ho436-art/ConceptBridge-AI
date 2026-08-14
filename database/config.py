"""
ConceptBridge AI - Database Configuration Module
Handles environment variables and connection configuration for SQLite and MySQL.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Attempt to load .env file if it exists, without strictly requiring python-dotenv
def _load_env_file():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val


_load_env_file()


@dataclass(frozen=True)
class DatabaseConfig:
    """Configuration settings for ConceptBridge AI database layer."""
    db_type: str = "sqlite"  # 'sqlite' or 'mysql'
    sqlite_path: str = "database/conceptbridge.db"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_db: str = "conceptbridge_ai"
    mysql_charset: str = "utf8mb4"
    hash_iterations: int = 100_000

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Builds DatabaseConfig from environment variables with sensible defaults."""
        db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
        sqlite_path = os.getenv("SQLITE_DB_PATH", os.getenv("DB_FILE_PATH", "database/conceptbridge.db"))
        
        # If relative path, resolve relative to project root
        if db_type == "sqlite" and not os.path.isabs(sqlite_path) and sqlite_path != ":memory:":
            project_root = Path(__file__).resolve().parent.parent
            sqlite_path = str(project_root / sqlite_path)

        return cls(
            db_type=db_type,
            sqlite_path=sqlite_path,
            mysql_host=os.getenv("DB_HOST", "127.0.0.1"),
            mysql_port=int(os.getenv("DB_PORT", "3306")),
            mysql_user=os.getenv("DB_USER", "root"),
            mysql_password=os.getenv("DB_PASSWORD", ""),
            mysql_db=os.getenv("DB_NAME", "conceptbridge_ai"),
            mysql_charset=os.getenv("DB_CHARSET", "utf8mb4"),
            hash_iterations=int(os.getenv("HASH_ITERATIONS", "100000")),
        )


_active_config: DatabaseConfig = DatabaseConfig.from_env()


def get_config() -> DatabaseConfig:
    """Gets the currently active DatabaseConfig."""
    global _active_config
    return _active_config


def set_config(new_config: DatabaseConfig) -> None:
    """Sets the active DatabaseConfig."""
    global _active_config
    _active_config = new_config
