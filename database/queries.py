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

def get_all_users(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all users in the system."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY username ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_topics(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all topics in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics ORDER BY title ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_db_learner_profile(user_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve learner profile for a specific user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM learner_profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_db_learner_profile(user_id: str, level: str, style: str, db_path: Optional[str] = None) -> None:
    """Update user learning level and style in database."""
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            """
            UPDATE learner_profiles 
            SET estimated_level = ?, preferred_learning_style = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (level, style, user_id)
        )
    conn.close()

def get_topic_mastery(user_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch topic mastery with titles for a user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT tm.*, t.title, t.category 
        FROM topic_mastery tm 
        JOIN topics t ON tm.topic_id = t.topic_id 
        WHERE tm.user_id = ?
        ORDER BY tm.mastery_score DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_learning_history(user_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve explanation history with titles for a user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT lh.*, t.title 
        FROM learning_history lh 
        JOIN topics t ON lh.topic_id = t.topic_id 
        WHERE lh.user_id = ? 
        ORDER BY lh.created_at DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_smart_refresh_history(user_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve break logs for a user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM smart_refresh_history WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_feedback(user_id: str, history_id: Optional[str], rating: int, feedback_type: str, comments: Optional[str] = None, db_path: Optional[str] = None) -> str:
    """Save user feedback on a concept explanation."""
    feedback_id = str(uuid.uuid4())
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            """
            INSERT INTO feedback (feedback_id, user_id, history_id, rating, feedback_type, comments)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (feedback_id, user_id, history_id, rating, feedback_type, comments)
        )
    conn.close()
    return feedback_id

def seed_topics_if_empty(db_path: Optional[str] = None) -> None:
    """Pre-populates default topics if the topics table is empty."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM topics")
    count = cursor.fetchone()[0]
    if count == 0:
        default_topics = [
            ("recursion", "Recursion", "Computer Science", "beginner", None),
            ("neural_networks", "Neural Networks", "Artificial Intelligence", "intermediate", None),
            ("pca", "Principal Component Analysis (PCA)", "Data Science", "intermediate", None),
            ("database_indexing", "Database Indexing", "Databases", "intermediate", None),
            ("git_version_control", "Git Version Control", "Software Engineering", "beginner", None),
        ]
        with conn:
            conn.executemany(
                "INSERT INTO topics (topic_id, title, category, difficulty_level, prerequisites) VALUES (?, ?, ?, ?, ?)",
                default_topics
            )
    conn.close()

def create_topic_if_not_exists(topic_id: str, title: str, category: str, db_path: Optional[str] = None) -> None:
    """Inserts a new topic if it does not already exist."""
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO topics (topic_id, title, category) VALUES (?, ?, ?)",
            (topic_id, title, category)
        )
    conn.close()


