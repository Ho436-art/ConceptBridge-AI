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
    log_smart_refresh,
    get_all_users,
    get_all_topics,
    get_db_learner_profile,
    update_db_learner_profile,
    get_topic_mastery,
    get_learning_history,
    get_smart_refresh_history,
    save_feedback,
    seed_topics_if_empty,
    create_topic_if_not_exists
)

__all__ = [
    "get_connection",
    "init_db",
    "create_user",
    "get_user",
    "save_learning_history",
    "update_mastery",
    "log_smart_refresh",
    "get_all_users",
    "get_all_topics",
    "get_db_learner_profile",
    "update_db_learner_profile",
    "get_topic_mastery",
    "get_learning_history",
    "get_smart_refresh_history",
    "save_feedback",
    "seed_topics_if_empty",
    "create_topic_if_not_exists"
]
