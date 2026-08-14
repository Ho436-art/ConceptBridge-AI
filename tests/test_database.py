"""
ConceptBridge AI - Database Layer Comprehensive Test Suite
Tests all required tables, constraints, security hashing, queries, and business helper functions.
Runs directly via Python's built-in `unittest` (0 dependencies) or `pytest`.
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from database.config import DatabaseConfig, get_config, set_config
from database.db import init_db, get_connection, get_db_cursor
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
    save_attempt,
    get_attempts_by_user,
    get_topic_mastery,
    update_topic_mastery,
    save_feedback,
    get_feedback_by_user,
    save_recommendation,
    get_recommendations,
    mark_recommendation_completed,
    save_refresh_session,
    get_refresh_sessions_by_user,
    get_recent_learning_history,
)


class TestConceptBridgeDatabase(unittest.TestCase):
    """Test suite covering the complete ConceptBridge AI database layer."""

    def setUp(self):
        """Sets up an isolated, temporary SQLite database for each test method."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = os.path.join(self.temp_dir.name, "test_conceptbridge.db")
        self.test_cfg = DatabaseConfig(db_type="sqlite", sqlite_path=self.test_db_path)

        self._orig_config = get_config()
        set_config(self.test_cfg)

        init_db(db_config=self.test_cfg)

    def tearDown(self):
        """Cleans up temporary resources."""
        set_config(self._orig_config)
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    # =========================================================================
    # 1. SECURITY & PASSWORD HASHING TESTS
    # =========================================================================

    def test_password_hashing_and_verification(self):
        """Verify password hashing produces salted hashes and resists plaintext leak."""
        pwd = "SuperSecretPassword123!"
        hashed = hash_password(pwd)

        self.assertTrue(hashed.startswith("pbkdf2_sha256$"))
        self.assertNotIn(pwd, hashed)  # Plaintext password is not exposed
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword!", hashed))
        self.assertFalse(verify_password("", hashed))
        self.assertFalse(verify_password(pwd, "invalid_hash_string"))

    # =========================================================================
    # 2. USER MANAGEMENT TESTS
    # =========================================================================

    def test_create_and_get_user(self):
        """Test user creation and lookup by ID and email."""
        user = create_user(
            name="Alice Walker",
            email="alice@example.com",
            password="ValidPassword789!",
            create_default_profile=True,
        )

        self.assertIsNotNone(user.user_id)
        self.assertEqual(user.name, "Alice Walker")
        self.assertEqual(user.email, "alice@example.com")
        self.assertTrue(user.password_hash.startswith("pbkdf2_sha256$"))

        # Lookup by ID
        by_id = get_user(user_id=user.user_id)
        self.assertIsNotNone(by_id)
        self.assertEqual(by_id.name, "Alice Walker")

        # Lookup by email
        by_email = get_user(email="alice@example.com")
        self.assertIsNotNone(by_email)
        self.assertEqual(by_email.user_id, user.user_id)

        # Verify default profile was created
        profile = get_learner_profile(user.user_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.preferred_level, "beginner")

    def test_user_credential_verification(self):
        """Test authentication verification helper."""
        create_user(name="Bob Smith", email="bob@example.com", password="MySecurePassword1!")

        authenticated = verify_user_credentials("bob@example.com", "MySecurePassword1!")
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.name, "Bob Smith")

        # Wrong password
        self.assertIsNone(verify_user_credentials("bob@example.com", "WrongPassword"))
        # Non-existent user
        self.assertIsNone(verify_user_credentials("nonexistent@example.com", "MySecurePassword1!"))

    def test_unique_email_constraint(self):
        """Test that creating a user with duplicate email raises an integrity error."""
        create_user(name="User One", email="unique@example.com", password="Password123!")
        with self.assertRaises(sqlite3.IntegrityError):
            create_user(name="User Two", email="unique@example.com", password="Password456!")

    def test_invalid_user_inputs(self):
        """Test validation on blank name, invalid email, and short password."""
        with self.assertRaises(ValueError):
            create_user(name="", email="test@example.com", password="Password123!")
        with self.assertRaises(ValueError):
            create_user(name="Valid Name", email="not-an-email", password="Password123!")
        with self.assertRaises(ValueError):
            create_user(name="Valid Name", email="test@example.com", password="123")

    # =========================================================================
    # 3. LEARNER PROFILE TESTS
    # =========================================================================

    def test_learner_profile_update(self):
        """Test updating learning preferences and levels."""
        user = create_user(name="Charlie", email="charlie@example.com", password="Password123!")

        updated = update_learner_profile(
            user_id=user.user_id,
            preferred_level="intermediate",
            learning_preference="analogy_first",
            overall_level="intermediate",
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.preferred_level, "intermediate")
        self.assertEqual(updated.learning_preference, "analogy_first")
        self.assertEqual(updated.overall_level, "intermediate")

        refetched = get_learner_profile(user.user_id)
        self.assertEqual(refetched.learning_preference, "analogy_first")

    # =========================================================================
    # 4. TOPICS & QUESTIONS TESTS
    # =========================================================================

    def test_topics_and_questions_management(self):
        """Test topic and question creation, listing, and filtering."""
        t1 = create_topic(
            topic_name="Recursion Basics",
            subject="Computer Science",
            difficulty="beginner",
            description="Core principles of recursion.",
        )
        t2 = create_topic(
            topic_name="Graph Traversal (BFS & DFS)",
            subject="Algorithms",
            difficulty="intermediate",
            description="Traversing trees and graphs.",
        )

        self.assertEqual(get_topic(t1.topic_id).topic_name, "Recursion Basics")

        # List all topics
        all_topics = list_topics()
        self.assertEqual(len(all_topics), 2)

        # Filter topics by subject
        algo_topics = list_topics(subject="Algorithms")
        self.assertEqual(len(algo_topics), 1)
        self.assertEqual(algo_topics[0].topic_name, "Graph Traversal (BFS & DFS)")

        # Add questions
        q1 = create_question(
            topic_id=t1.topic_id,
            question_text="What is a base case?",
            answer="A terminating condition.",
            difficulty="beginner",
            explanation="Stops recursion from continuing infinitely.",
        )
        q2 = create_question(
            topic_id=t1.topic_id,
            question_text="What happens during stack overflow?",
            answer="Call stack exceeds memory limit.",
            difficulty="intermediate",
        )

        questions = get_questions_by_topic(t1.topic_id)
        self.assertEqual(len(questions), 2)

        beginner_q = get_questions_by_topic(t1.topic_id, difficulty="beginner")
        self.assertEqual(len(beginner_q), 1)
        self.assertEqual(beginner_q[0].question_id, q1.question_id)

    # =========================================================================
    # 5. LEARNING SESSIONS TESTS
    # =========================================================================

    def test_save_learning_session_and_constraints(self):
        """Test saving learning sessions and duration constraint."""
        user = create_user(name="Dave", email="dave@example.com", password="Password123!")
        topic = create_topic(topic_name="Binary Search", subject="Algorithms", difficulty="beginner")

        session = save_learning_session(
            user_id=user.user_id,
            topic_id=topic.topic_id,
            started_at="2026-08-14 10:00:00",
            ended_at="2026-08-14 10:20:00",
            duration=1200,
        )
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.duration, 1200)

        # Negative duration validation in Python layer
        with self.assertRaises(ValueError):
            save_learning_session(
                user_id=user.user_id,
                topic_id=topic.topic_id,
                duration=-50,
            )

    # =========================================================================
    # 6. ATTEMPTS & METRICS TESTS
    # =========================================================================

    def test_save_and_query_attempts(self):
        """Test recording question attempts and querying user history."""
        user = create_user(name="Eve", email="eve@example.com", password="Password123!")
        topic = create_topic(topic_name="Hashing", subject="Data Structures", difficulty="beginner")
        question = create_question(
            topic_id=topic.topic_id,
            question_text="What is a hash collision?",
            answer="When two distinct keys produce the same hash code.",
        )

        att1 = save_attempt(
            user_id=user.user_id,
            topic_id=topic.topic_id,
            question_id=question.question_id,
            answer="Two keys have same hash.",
            correct=True,
            response_time=3200,
        )
        att2 = save_attempt(
            user_id=user.user_id,
            topic_id=topic.topic_id,
            question_id=question.question_id,
            answer="Memory overflow.",
            correct=False,
            response_time=4500,
        )

        self.assertTrue(att1.correct)
        self.assertFalse(att2.correct)

        history = get_attempts_by_user(user.user_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].question_text, "What is a hash collision?")

    # =========================================================================
    # 7. TOPIC MASTERY TESTS
    # =========================================================================

    def test_topic_mastery_upsert_and_bounds(self):
        """Test topic mastery tracking and score bounds validation."""
        user = create_user(name="Frank", email="frank@example.com", password="Password123!")
        topic = create_topic(topic_name="OOP Principles", subject="Programming", difficulty="beginner")

        # Initial mastery
        m1 = update_topic_mastery(
            user_id=user.user_id,
            topic_id=topic.topic_id,
            mastery_score=0.65,
            confidence=0.70,
        )
        self.assertEqual(m1.mastery_score, 0.65)

        # Upsert (update existing score)
        m2 = update_topic_mastery(
            user_id=user.user_id,
            topic_id=topic.topic_id,
            mastery_score=0.90,
            confidence=0.95,
        )
        self.assertEqual(m2.mastery_score, 0.90)

        # Retrieve single topic mastery
        fetched = get_topic_mastery(user.user_id, topic.topic_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.mastery_score, 0.90)

        # Out of bounds validation
        with self.assertRaises(ValueError):
            update_topic_mastery(user.user_id, topic.topic_id, mastery_score=1.5, confidence=0.5)
        with self.assertRaises(ValueError):
            update_topic_mastery(user.user_id, topic.topic_id, mastery_score=0.5, confidence=-0.1)

    # =========================================================================
    # 8. FEEDBACK TESTS
    # =========================================================================

    def test_save_and_query_feedback(self):
        """Test learner feedback submission and valid feedback types."""
        user = create_user(name="Grace", email="grace@example.com", password="Password123!")
        topic = create_topic(topic_name="Async/Await", subject="Programming", difficulty="intermediate")

        fb = save_feedback(
            user_id=user.user_id,
            topic_id=topic.topic_id,
            feedback_type="got_it",
        )
        self.assertEqual(fb.feedback_type, "got_it")

        # Query feedback
        fb_list = get_feedback_by_user(user.user_id)
        self.assertEqual(len(fb_list), 1)
        self.assertEqual(fb_list[0].topic_name, "Async/Await")

        # Invalid feedback type rejection
        with self.assertRaises(ValueError):
            save_feedback(user.user_id, topic.topic_id, feedback_type="invalid_type")

    # =========================================================================
    # 9. RECOMMENDATION TESTS
    # =========================================================================

    def test_recommendations_workflow(self):
        """Test generating, querying pending, and marking recommendations completed."""
        user = create_user(name="Heidi", email="heidi@example.com", password="Password123!")
        topic = create_topic(topic_name="Tree Balancing", subject="Algorithms", difficulty="advanced")

        rec = save_recommendation(
            user_id=user.user_id,
            topic_id=topic.topic_id,
            recommendation_type="interactive_demo",
            reason="Practice AVL tree rotations interactively.",
            completed=False,
        )
        self.assertFalse(rec.completed)

        pending = get_recommendations(user.user_id, pending_only=True)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].recommendation_id, rec.recommendation_id)

        # Mark completed
        success = mark_recommendation_completed(rec.recommendation_id)
        self.assertTrue(success)

        pending_after = get_recommendations(user.user_id, pending_only=True)
        self.assertEqual(len(pending_after), 0)

        all_recs = get_recommendations(user.user_id, pending_only=False)
        self.assertEqual(len(all_recs), 1)
        self.assertTrue(all_recs[0].completed)

    # =========================================================================
    # 10. REFRESH SESSIONS TESTS (Smart Refresh)
    # =========================================================================

    def test_refresh_sessions_and_constraints(self):
        """Test Smart Refresh sessions tracking and duration constraint."""
        user = create_user(name="Ivan", email="ivan@example.com", password="Password123!")

        ref = save_refresh_session(
            user_id=user.user_id,
            activity_type="spaced_repetition_quiz",
            started_at="2026-08-14 12:00:00",
            ended_at="2026-08-14 12:08:00",
            duration=480,
            completed=True,
        )
        self.assertTrue(ref.completed)
        self.assertEqual(ref.duration, 480)

        history = get_refresh_sessions_by_user(user.user_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].activity_type, "spaced_repetition_quiz")

        # Negative duration check
        with self.assertRaises(ValueError):
            save_refresh_session(user.user_id, "flashcards", duration=-10)

    # =========================================================================
    # 11. AGGREGATED LEARNING HISTORY TESTS
    # =========================================================================

    def test_get_recent_learning_history(self):
        """Test aggregated learning history compilation."""
        user = create_user(name="Judy", email="judy@example.com", password="Password123!")
        topic = create_topic(topic_name="Bit Manipulation", subject="Computer Science", difficulty="intermediate")
        q = create_question(topic_id=topic.topic_id, question_text="What does XOR do?", answer="Returns 1 if bits differ.")

        save_learning_session(user.user_id, topic.topic_id, duration=600)
        save_attempt(user.user_id, topic.topic_id, q.question_id, answer="Diff bits", correct=True, response_time=2500)
        save_feedback(user.user_id, topic.topic_id, feedback_type="got_it")
        update_topic_mastery(user.user_id, topic.topic_id, mastery_score=0.85, confidence=0.90)
        save_refresh_session(user.user_id, activity_type="quick_drill", duration=180, completed=True)

        summary = get_recent_learning_history(user.user_id)

        self.assertEqual(summary["user_id"], user.user_id)
        self.assertEqual(len(summary["recent_learning_sessions"]), 1)
        self.assertEqual(summary["attempt_stats"]["total_attempts"], 1)
        self.assertEqual(summary["attempt_stats"]["correct_attempts"], 1)
        self.assertEqual(summary["attempt_stats"]["accuracy_percent"], 100.0)
        self.assertEqual(summary["feedback_distribution"].get("got_it"), 1)
        self.assertEqual(len(summary["recent_refresh_sessions"]), 1)
        self.assertEqual(len(summary["topic_mastery_overview"]), 1)
        self.assertEqual(summary["topic_mastery_overview"][0]["mastery_score"], 0.85)

    # =========================================================================
    # 12. FOREIGN KEY ENFORCEMENT & INTEGRITY TESTS
    # =========================================================================

    def test_foreign_key_constraints(self):
        """Verify SQLite foreign key enforcement on invalid references."""
        # Inserting learning session for non-existent user should fail
        with self.assertRaises(sqlite3.IntegrityError):
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    "INSERT INTO learning_sessions (session_id, user_id, topic_id, started_at) VALUES (?, ?, ?, ?);",
                    ("fake_session", "non_existent_user", "non_existent_topic", "2026-08-14 00:00:00")
                )


if __name__ == "__main__":
    unittest.main()
