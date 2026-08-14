"""
ConceptBridge AI - Development Seed Data Script
Populates the database with realistic sample topics, questions, learner profiles,
and historical interactions for development and testing.

Usage:
    python -m database.seed
    or
    python database/seed.py
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path when running script directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.db import init_db, reset_db
from database.queries import (
    create_user,
    update_learner_profile,
    create_topic,
    create_question,
    save_learning_session,
    save_attempt,
    update_topic_mastery,
    save_feedback,
    save_recommendation,
    save_refresh_session,
)


def safe_print(msg: str):
    """Safely prints messages on all operating systems without UnicodeEncodeError."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def seed_development_data(reset_first: bool = True):
    """
    Seeds development data with rich, realistic computer science & AI concepts.
    """
    safe_print("[INFO] Initializing database schema...")
    if reset_first:
        reset_db()
    else:
        init_db()

    safe_print("[INFO] Seeding Topics...")
    topics_data = [
        {
            "topic_id": "top_recursion",
            "topic_name": "Recursion & The Call Stack",
            "subject": "Computer Science",
            "difficulty": "beginner",
            "description": "Understanding base cases, recursive steps, and how the system call stack tracks function frames.",
        },
        {
            "topic_id": "top_backprop",
            "topic_name": "Neural Network Backpropagation",
            "subject": "Artificial Intelligence",
            "difficulty": "intermediate",
            "description": "How the chain rule of calculus computes gradients to update weights in multi-layer perceptrons.",
        },
        {
            "topic_id": "top_sql_index",
            "topic_name": "Database Indexing & B-Trees",
            "subject": "Databases",
            "difficulty": "intermediate",
            "description": "Optimizing relational database queries using B-Tree indexing, composite indexes, and lookup complexity.",
        },
        {
            "topic_id": "top_dynamic_prog",
            "topic_name": "Dynamic Programming & Memoization",
            "subject": "Algorithms",
            "difficulty": "advanced",
            "description": "Breaking down overlapping subproblems with optimal substructure using top-down and bottom-up techniques.",
        },
        {
            "topic_id": "top_memory_gc",
            "topic_name": "Memory Management & Garbage Collection",
            "subject": "Systems Programming",
            "difficulty": "beginner",
            "description": "Stack vs Heap allocation, reference counting, and generational garbage collection mechanisms.",
        },
    ]

    created_topics = {}
    for t in topics_data:
        topic = create_topic(
            topic_id=t["topic_id"],
            topic_name=t["topic_name"],
            subject=t["subject"],
            difficulty=t["difficulty"],
            description=t["description"],
        )
        created_topics[t["topic_id"]] = topic
        safe_print(f"  + Added Topic: {topic.topic_name} ({topic.subject})")

    safe_print("[INFO] Seeding Questions...")
    questions_data = [
        # Recursion
        {
            "question_id": "q_rec_01",
            "topic_id": "top_recursion",
            "question_text": "What condition must every recursive function define to prevent infinite recursion?",
            "difficulty": "beginner",
            "answer": "Base case",
            "explanation": "A base case specifies the condition under which the function returns a value directly without making further recursive calls.",
        },
        {
            "question_id": "q_rec_02",
            "topic_id": "top_recursion",
            "question_text": "Which memory region grows with each nested recursive call before returning?",
            "difficulty": "beginner",
            "answer": "Call stack",
            "explanation": "Each recursive call allocates a new stack frame on the call stack storing parameters and local variables.",
        },
        # Backpropagation
        {
            "question_id": "q_bp_01",
            "topic_id": "top_backprop",
            "question_text": "Which fundamental calculus rule allows gradients to propagate backward across nested layers?",
            "difficulty": "intermediate",
            "answer": "Chain rule",
            "explanation": "The chain rule allows computing the derivative of composite functions by multiplying derivatives of adjacent layers.",
        },
        # SQL Indexing
        {
            "question_id": "q_sql_01",
            "topic_id": "top_sql_index",
            "question_text": "What is the average search time complexity in a balanced B-Tree index with N records?",
            "difficulty": "intermediate",
            "answer": "O(log N)",
            "explanation": "B-Trees keep keys sorted in balanced hierarchical nodes, giving logarithmic lookup and insertion time.",
        },
    ]

    created_questions = {}
    for q in questions_data:
        question = create_question(
            question_id=q["question_id"],
            topic_id=q["topic_id"],
            question_text=q["question_text"],
            difficulty=q["difficulty"],
            answer=q["answer"],
            explanation=q["explanation"],
        )
        created_questions[q["question_id"]] = question
        safe_print(f"  + Added Question: {question.question_text[:50]}...")

    safe_print("[INFO] Seeding Demo Users & Learner Profiles...")
    # User 1: Alex (Visual Learner, Novice)
    user1 = create_user(
        name="Alex Mercer",
        email="alex.mercer@conceptbridge.dev",
        password="Password123!",
        user_id="usr_alex_001",
    )
    update_learner_profile(
        user_id=user1.user_id,
        preferred_level="beginner",
        learning_preference="visual",
        overall_level="novice",
    )
    safe_print(f"  + Created User: {user1.name} ({user1.email})")

    # User 2: Sarah (Step-by-step Learner, Intermediate)
    user2 = create_user(
        name="Sarah Chen",
        email="sarah.chen@conceptbridge.dev",
        password="SecurePass456!",
        user_id="usr_sarah_002",
    )
    update_learner_profile(
        user_id=user2.user_id,
        preferred_level="intermediate",
        learning_preference="step_by_step",
        overall_level="intermediate",
    )
    safe_print(f"  + Created User: {user2.name} ({user2.email})")

    safe_print("[INFO] Seeding Learning Sessions, Attempts, and Mastery for Alex...")
    # Learning session 1: Recursion
    save_learning_session(
        user_id=user1.user_id,
        topic_id="top_recursion",
        started_at="2026-08-14 10:00:00",
        ended_at="2026-08-14 10:25:00",
        duration=1500,  # 25 minutes
    )
    # Attempts
    save_attempt(
        user_id=user1.user_id,
        topic_id="top_recursion",
        question_id="q_rec_01",
        answer="Base case",
        correct=True,
        response_time=4200,  # 4.2 seconds
    )
    save_attempt(
        user_id=user1.user_id,
        topic_id="top_recursion",
        question_id="q_rec_02",
        answer="Heap memory",
        correct=False,
        response_time=8500,
    )
    # Mastery
    update_topic_mastery(
        user_id=user1.user_id,
        topic_id="top_recursion",
        mastery_score=0.75,
        confidence=0.80,
    )
    # Feedback
    save_feedback(
        user_id=user1.user_id,
        topic_id="top_recursion",
        feedback_type="almost",
    )
    # Recommendation
    save_recommendation(
        user_id=user1.user_id,
        topic_id="top_recursion",
        recommendation_type="interactive_visualizer",
        reason="Practice call stack visualization to reinforce stack frame lifecycle.",
    )
    # Smart Refresh Session
    save_refresh_session(
        user_id=user1.user_id,
        activity_type="flashcards_drill",
        started_at="2026-08-14 14:00:00",
        ended_at="2026-08-14 14:05:00",
        duration=300,
        completed=True,
    )

    safe_print("[INFO] Seeding Data for Sarah...")
    # Sarah's mastery on Backpropagation & SQL Indexing
    update_topic_mastery(
        user_id=user2.user_id,
        topic_id="top_backprop",
        mastery_score=0.92,
        confidence=0.95,
    )
    update_topic_mastery(
        user_id=user2.user_id,
        topic_id="top_sql_index",
        mastery_score=0.88,
        confidence=0.90,
    )
    save_feedback(
        user_id=user2.user_id,
        topic_id="top_backprop",
        feedback_type="got_it",
    )
    save_feedback(
        user_id=user2.user_id,
        topic_id="top_dynamic_prog",
        feedback_type="still_confused",
    )
    save_recommendation(
        user_id=user2.user_id,
        topic_id="top_dynamic_prog",
        recommendation_type="analogy_deep_dive",
        reason="Start with memoized Fibonacci before advancing to 2D grid pathing.",
    )

    safe_print("[SUCCESS] Development seed data successfully populated!")


if __name__ == "__main__":
    seed_development_data(reset_first=True)
