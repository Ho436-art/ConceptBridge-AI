"""
ConceptBridge AI - Database Layer Public Package API
Provides a clean, declarative interface for AI and UI developers without exposing raw SQL.
"""

from database.config import DatabaseConfig, get_config, set_config
from database.db import get_connection, get_db_cursor, get_db_connection, init_db, reset_db
from database.models import (
    User,
    LearnerProfile,
    Topic,
    Question,
    LearningSession,
    Attempt,
    TopicMastery,
    Feedback,
    Recommendation,
    RefreshSession,
)
from database.security import hash_password, verify_password
from database.queries import (
    create_user,
    get_user,
    verify_user_credentials,
    create_learner_profile,
    get_learner_profile,
    update_learner_profile,
    create_topic,
    get_topic,
    list_topics,
    create_question,
    get_question,
    get_questions_by_topic,
    save_learning_session,
    save_learning_history,
    save_attempt,
    get_attempts_by_user,
    get_topic_mastery,
    update_topic_mastery,
    update_mastery,
    save_feedback,
    get_feedback_by_user,
    save_recommendation,
    get_recommendations,
    mark_recommendation_completed,
    save_refresh_session,
    log_smart_refresh,
    get_refresh_sessions_by_user,
    get_recent_learning_history,
    get_all_users,
    get_all_topics,
    get_db_learner_profile,
    update_db_learner_profile,
    get_learning_history,
    get_smart_refresh_history,
    create_topic_if_not_exists,
)

__all__ = [
    # Configuration & Database Management
    "DatabaseConfig",
    "get_config",
    "set_config",
    "get_connection",
    "get_db_cursor",
    "get_db_connection",
    "init_db",
    "reset_db",
    # Security
    "hash_password",
    "verify_password",
    # Data Models
    "User",
    "LearnerProfile",
    "Topic",
    "Question",
    "LearningSession",
    "Attempt",
    "TopicMastery",
    "Feedback",
    "Recommendation",
    "RefreshSession",
    # User Management
    "create_user",
    "get_user",
    "verify_user_credentials",
    # Learner Profile
    "create_learner_profile",
    "get_learner_profile",
    "update_learner_profile",
    # Topics & Questions
    "create_topic",
    "get_topic",
    "list_topics",
    "create_question",
    "get_question",
    "get_questions_by_topic",
    # Learning Sessions & Attempts
    "save_learning_session",
    "save_learning_history",
    "save_attempt",
    "get_attempts_by_user",
    # Topic Mastery
    "get_topic_mastery",
    "update_topic_mastery",
    "update_mastery",
    # Feedback
    "save_feedback",
    "get_feedback_by_user",
    # Recommendations
    "save_recommendation",
    "get_recommendations",
    "mark_recommendation_completed",
    # Smart Refresh
    "save_refresh_session",
    "log_smart_refresh",
    "get_refresh_sessions_by_user",
    # Learning History
    "get_recent_learning_history",
    # UI Helpers
    "get_all_users",
    "get_all_topics",
    "get_db_learner_profile",
    "update_db_learner_profile",
    "get_learning_history",
    "get_smart_refresh_history",
    "create_topic_if_not_exists",
]
