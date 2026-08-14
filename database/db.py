"""
Centralized Database Connection & Transaction Manager
Owner: Member 3 (Database)
ConceptBridge AI - Centralized Database Connection & Transaction Manager
Provides connection pooling, context managers for safe transactions, and DDL initialization.
Designed for SQLite with seamless abstraction for MySQL transition.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Any, Optional, Union

from database.config import DatabaseConfig, get_config

DEFAULT_DB_PATH = os.getenv("DB_FILE_PATH", "database/conceptbridge.db")


def get_connection(
    db_config: Optional[Union[DatabaseConfig, str]] = None,
    db_path: Optional[str] = None
):
    """
    Creates and returns a new database connection based on configuration.
    For SQLite: automatically sets row_factory = sqlite3.Row and enables foreign keys.
    For MySQL: connects via PyMySQL or mysql.connector.
    """
    if isinstance(db_config, str):
        path = db_config
        cfg = DatabaseConfig(db_type="sqlite", sqlite_path=path)
    elif db_path is not None:
        cfg = DatabaseConfig(db_type="sqlite", sqlite_path=db_path)
    elif isinstance(db_config, DatabaseConfig):
        cfg = db_config
    else:
        cfg = get_config()

    if cfg.db_type == "sqlite":
        # Ensure parent directory exists for file-based SQLite
        if cfg.sqlite_path != ":memory:":
            db_file = Path(cfg.sqlite_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(cfg.sqlite_path, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        # Crucial: enable foreign key constraints in SQLite per connection
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    elif cfg.db_type == "mysql":
        try:
            import pymysql
            from pymysql.cursors import DictCursor

            return pymysql.connect(
                host=cfg.mysql_host,
                port=cfg.mysql_port,
                user=cfg.mysql_user,
                password=cfg.mysql_password,
                database=cfg.mysql_db,
                charset=cfg.mysql_charset,
                cursorclass=DictCursor,
                autocommit=False,
                )
            )
        except ImportError:
            raise ImportError(
                "PyMySQL is required for MySQL support. Install it with 'pip install pymysql'."
            )
    else:
        raise ValueError(f"Unsupported database type: {cfg.db_type}")


@contextmanager
def get_db_cursor(
    commit: bool = False,
    db_config: Optional[Union[DatabaseConfig, str]] = None,
    conn: Optional[Any] = None,
    db_path: Optional[str] = None
) -> Generator[Any, None, None]:
    """
    Context manager that yields a cursor and manages commit/rollback and connection closing.
    If an external connection is provided, it reuses it without closing it.
    """
    owns_conn = conn is None
    connection = conn if conn is not None else get_connection(db_config=db_config, db_path=db_path)
    cursor = connection.cursor()
    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        if owns_conn:
            connection.close()


@contextmanager
def get_db_connection(
    commit: bool = False,
    db_config: Optional[Union[DatabaseConfig, str]] = None,
    db_path: Optional[str] = None
) -> Generator[Any, None, None]:
    """
    Context manager yielding a connection instance.
    """
    connection = get_connection(db_config=db_config, db_path=db_path)
    try:
        yield connection
        if commit:
            connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db(
    db_path: Optional[str] = None,
    schema_path: Optional[str] = None,
    db_config: Optional[DatabaseConfig] = None
) -> None:
    """
    Initializes database schema by executing schema.sql DDL script.
    """
    if db_path is not None:
        cfg = DatabaseConfig(db_type="sqlite", sqlite_path=db_path)
    else:
        cfg = db_config or get_config()

    if schema_path is None:
        schema_path = str(Path(__file__).resolve().parent / "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db_connection(commit=True, db_config=cfg) as conn:
        if cfg.db_type == "sqlite":
            conn.executescript(schema_sql)
        elif cfg.db_type == "mysql":
            with conn.cursor() as cursor:
                # Split commands by semicolon for MySQL
                for statement in schema_sql.split(";"):
                    stmt = statement.strip()
                    if stmt and not stmt.lower().startswith("pragma"):
                        cursor.execute(stmt)


def reset_db(db_config: Optional[DatabaseConfig] = None, db_path: Optional[str] = None) -> None:
    """
    Resets the database by dropping existing tables and recreating schema.
    """
    if db_path is not None:
        cfg = DatabaseConfig(db_type="sqlite", sqlite_path=db_path)
    else:
        cfg = db_config or get_config()

    if cfg.db_type == "sqlite" and cfg.sqlite_path != ":memory:":
        if os.path.exists(cfg.sqlite_path):
            try:
                os.remove(cfg.sqlite_path)
            except PermissionError:
                pass
    init_db(db_config=cfg)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
