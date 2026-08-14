"""
Database Module for ConceptBridge AI.
Owner: Member 3 (Database)

Handles SQLite/PostgreSQL connection management, schema initialization,
and persistence queries for users, learner profiles, mastery, and refresh logs.
"""

from .db import get_connection, init_db
from .queries import (
    create_user,
    get_user,
    save_learning_history,
    update_mastery,
    log_smart_refresh
)

__all__ = [
    "get_connection",
    "init_db",
    "create_user",
    "get_user",
    "save_learning_history",
    "update_mastery",
    "log_smart_refresh"
]
