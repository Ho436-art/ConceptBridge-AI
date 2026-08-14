"""
Database Connector Module
Owner: Member 3 (Database)

Handles database connection management, initialization, and session creation.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = os.getenv("DB_FILE_PATH", "database/conceptbridge.db")

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Returns a SQLite connection object with row factory set to sqlite3.Row.
    """
    path = db_path or DEFAULT_DB_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[str] = None, schema_path: Optional[str] = None) -> None:
    """
    Initializes database tables from schema.sql.
    """
    path = db_path or DEFAULT_DB_PATH
    schema_file = schema_path or os.path.join(os.path.dirname(__file__), "schema.sql")
    
    conn = get_connection(path)
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    with conn:
        conn.executescript(schema_sql)
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
