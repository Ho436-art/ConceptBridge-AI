"""
Database Queries Module
Owner: Member 3 (Database)

Clean, parameterized SQL query helper functions.
Separation of Concerns Rule: No direct UI or AI generation code in queries.
"""

import sqlite3
import uuid
from typing import Dict, Any, Optional, List
from .db import get_connection

def create_user(username: str, email: Optional[str] = None, db_path: Optional[str] = None) -> str:
    """Create a new user and initialize their learner profile."""
    user_id = str(uuid.uuid4())
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)",
            (user_id, username, email)
        )
        conn.execute(
            "INSERT INTO learner_profiles (profile_id, user_id) VALUES (?, ?)",
            (str(uuid.uuid4()), user_id)
        )
    conn.close()
    return user_id

def get_user(user_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve user details by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_learning_history(user_id: str, topic_id: str, concept_query: str,
                          analogy: str, level: str, time_spent: int,
                          db_path: Optional[str] = None) -> str:
    """Record an interaction with the teaching engine."""
    history_id = str(uuid.uuid4())
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            """
            INSERT INTO learning_history 
            (history_id, user_id, topic_id, concept_query, analogy_presented, explanation_level, time_spent_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (history_id, user_id, topic_id, concept_query, analogy, level, time_spent)
        )
    conn.close()
    return history_id

def update_mastery(user_id: str, topic_id: str, score_delta: float, db_path: Optional[str] = None) -> None:
    """Update topic mastery score."""
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            """
            INSERT INTO topic_mastery (mastery_id, user_id, topic_id, mastery_score)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, topic_id) DO UPDATE SET
                mastery_score = MIN(1.0, MAX(0.0, mastery_score + ?)),
                last_reviewed = CURRENT_TIMESTAMP
            """,
            (str(uuid.uuid4()), user_id, topic_id, max(0.0, score_delta), score_delta)
        )
    conn.close()

def log_smart_refresh(user_id: str, activity_type: str, duration_seconds: int, db_path: Optional[str] = None) -> str:
    """Log a completed Smart Refresh activity."""
    refresh_id = str(uuid.uuid4())
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            """
            INSERT INTO smart_refresh_history (refresh_id, user_id, activity_type, duration_seconds)
            VALUES (?, ?, ?, ?)
            """,
            (refresh_id, user_id, activity_type, min(300, duration_seconds))
        )
    conn.close()
    return refresh_id
