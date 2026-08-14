"""
ConceptBridge AI - Database Access Layer & Queries Repository
Clean, parameterized database access functions separating SQL from AI and UI business logic.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union

from database.db import get_db_cursor
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


def _generate_id() -> str:
    """Generates a UUID4 string."""
    return str(uuid.uuid4())


def _current_timestamp() -> str:
    """Returns current UTC timestamp in ISO8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# =============================================================================
# 1. USER MANAGEMENT FUNCTIONS
# =============================================================================

def create_user(
    name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    user_id: Optional[str] = None,
    create_default_profile: bool = True,
    username: Optional[str] = None,
    db_path: Optional[str] = None,
) -> User:
    """
    Creates a new user account with a salted password hash.
    Optionally creates a default beginner learner profile.
    """
    final_name = name or username
    if not final_name or not final_name.strip():
        raise ValueError("User name cannot be empty.")

    clean_name = final_name.strip()
    clean_email = email.strip().lower() if email and email.strip() else f"{clean_name.lower().replace(' ', '_')}@conceptbridge.local"

    if email and "@" not in email:
        raise ValueError("Valid email address is required.")

    final_password = password if password else "ConceptBridgeDefaultPass123!"
    if len(final_password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    uid = user_id or _generate_id()
    pwd_hash = hash_password(final_password)
    created_at = _current_timestamp()

    sql = """
        INSERT INTO users (user_id, name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?);
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (uid, clean_name, clean_email, pwd_hash, created_at))

    user = User(
        user_id=uid,
        name=clean_name,
        email=clean_email,
        created_at=created_at,
        password_hash=pwd_hash,
    )

    if create_default_profile:
        create_learner_profile(user_id=uid, db_path=db_path)

    return user


def get_user(
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    db_path: Optional[str] = None
) -> Optional[User]:
    """
    Retrieves a user by user_id or email.
    """
    if not user_id and not email:
        raise ValueError("Either user_id or email must be provided.")

    if user_id:
        sql = "SELECT user_id, name, email, password_hash, created_at FROM users WHERE user_id = ?;"
        params = (user_id,)
    else:
        sql = "SELECT user_id, name, email, password_hash, created_at FROM users WHERE email = ?;"
        params = (email.strip().lower(),)

    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        if not row:
            return None
        return User(
            user_id=row["user_id"],
            name=row["name"],
            email=row["email"],
            created_at=str(row["created_at"]),
            password_hash=row["password_hash"],
        )


def verify_user_credentials(email: str, password: str, db_path: Optional[str] = None) -> Optional[User]:
    """
    Verifies user login credentials. Returns User if valid, None otherwise.
    """
    if not email or not password:
        return None

    user = get_user(email=email, db_path=db_path)
    if not user or not user.password_hash:
        return None

    if verify_password(password, user.password_hash):
        return user
    return None


# =============================================================================
# 2. LEARNER PROFILE FUNCTIONS
# =============================================================================

def create_learner_profile(
    user_id: str,
    preferred_level: str = "beginner",
    learning_preference: str = "step_by_step",
    overall_level: str = "novice",
    profile_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> LearnerProfile:
    """
    Creates a personalized learner profile for an existing user.
    """
    pid = profile_id or _generate_id()
    now = _current_timestamp()

    sql = """
        INSERT INTO learner_profiles (
            profile_id, user_id, preferred_level, learning_preference, overall_level, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(
            sql,
            (pid, user_id, preferred_level, learning_preference, overall_level, now, now)
        )

    return LearnerProfile(
        profile_id=pid,
        user_id=user_id,
        preferred_level=preferred_level,
        learning_preference=learning_preference,
        overall_level=overall_level,
        created_at=now,
        updated_at=now,
    )


def get_learner_profile(user_id: str, db_path: Optional[str] = None) -> Optional[LearnerProfile]:
    """
    Retrieves the learner profile for a given user_id.
    """
    sql = """
        SELECT profile_id, user_id, preferred_level, learning_preference, overall_level, created_at, updated_at
        FROM learner_profiles
        WHERE user_id = ?;
    """
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return LearnerProfile(
            profile_id=row["profile_id"],
            user_id=row["user_id"],
            preferred_level=row["preferred_level"],
            learning_preference=row["learning_preference"],
            overall_level=row["overall_level"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )


def update_learner_profile(
    user_id: str,
    preferred_level: Optional[str] = None,
    learning_preference: Optional[str] = None,
    overall_level: Optional[str] = None,
    db_path: Optional[str] = None
) -> Optional[LearnerProfile]:
    """
    Updates learner profile attributes.
    """
    existing = get_learner_profile(user_id, db_path=db_path)
    if not existing:
        return None

    new_preferred = preferred_level if preferred_level is not None else existing.preferred_level
    new_pref_style = learning_preference if learning_preference is not None else existing.learning_preference
    new_overall = overall_level if overall_level is not None else existing.overall_level
    updated_at = _current_timestamp()

    sql = """
        UPDATE learner_profiles
        SET preferred_level = ?, learning_preference = ?, overall_level = ?, updated_at = ?
        WHERE user_id = ?;
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (new_preferred, new_pref_style, new_overall, updated_at, user_id))

    return LearnerProfile(
        profile_id=existing.profile_id,
        user_id=user_id,
        preferred_level=new_preferred,
        learning_preference=new_pref_style,
        overall_level=new_overall,
        created_at=existing.created_at,
        updated_at=updated_at,
    )


# =============================================================================
# 3. TOPIC & QUESTION MANAGEMENT FUNCTIONS
# =============================================================================

def create_topic(
    topic_name: str,
    subject: str,
    difficulty: str = "beginner",
    description: Optional[str] = None,
    topic_id: Optional[str] = None,
    title: Optional[str] = None,
    category: Optional[str] = None,
    db_path: Optional[str] = None,
) -> Topic:
    """
    Registers a new concept/topic in the catalog.
    """
    name = topic_name or title
    subj = subject or category or "General"
    tid = topic_id or _generate_id()
    sql = """
        INSERT INTO topics (topic_id, topic_name, subject, difficulty, description)
        VALUES (?, ?, ?, ?, ?);
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (tid, name.strip(), subj.strip(), difficulty.strip(), description))

    return Topic(
        topic_id=tid,
        topic_name=name.strip(),
        subject=subj.strip(),
        difficulty=difficulty.strip(),
        description=description,
    )


def get_topic(topic_id: str, db_path: Optional[str] = None) -> Optional[Topic]:
    """
    Retrieves topic details by topic_id.
    """
    sql = "SELECT topic_id, topic_name, subject, difficulty, description FROM topics WHERE topic_id = ?;"
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, (topic_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Topic(
            topic_id=row["topic_id"],
            topic_name=row["topic_name"],
            subject=row["subject"],
            difficulty=row["difficulty"],
            description=row["description"],
        )


def list_topics(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Topic]:
    """
    Lists topics with optional filtering by subject or difficulty.
    """
    conditions = []
    params: List[Any] = []

    if subject:
        conditions.append("subject = ?")
        params.append(subject.strip())
    if difficulty:
        conditions.append("difficulty = ?")
        params.append(difficulty.strip())

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT topic_id, topic_name, subject, difficulty, description FROM topics {where_clause} ORDER BY subject, topic_name;"

    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        return [
            Topic(
                topic_id=row["topic_id"],
                topic_name=row["topic_name"],
                subject=row["subject"],
                difficulty=row["difficulty"],
                description=row["description"],
            )
            for row in rows
        ]


def create_question(
    topic_id: str,
    question_text: str,
    answer: str,
    difficulty: str = "beginner",
    explanation: Optional[str] = None,
    question_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> Question:
    """
    Creates an assessment question for a given topic.
    """
    qid = question_id or _generate_id()
    sql = """
        INSERT INTO questions (question_id, topic_id, question_text, difficulty, answer, explanation)
        VALUES (?, ?, ?, ?, ?, ?);
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (qid, topic_id, question_text.strip(), difficulty.strip(), answer.strip(), explanation))

    return Question(
        question_id=qid,
        topic_id=topic_id,
        question_text=question_text.strip(),
        difficulty=difficulty.strip(),
        answer=answer.strip(),
        explanation=explanation,
    )


def get_question(question_id: str, db_path: Optional[str] = None) -> Optional[Question]:
    """
    Retrieves a single question by question_id.
    """
    sql = "SELECT question_id, topic_id, question_text, difficulty, answer, explanation FROM questions WHERE question_id = ?;"
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, (question_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Question(
            question_id=row["question_id"],
            topic_id=row["topic_id"],
            question_text=row["question_text"],
            difficulty=row["difficulty"],
            answer=row["answer"],
            explanation=row["explanation"],
        )


def get_questions_by_topic(
    topic_id: str,
    difficulty: Optional[str] = None,
    db_path: Optional[str] = None
) -> List[Question]:
    """
    Retrieves questions for a topic, optionally filtered by difficulty.
    """
    if difficulty:
        sql = """
            SELECT question_id, topic_id, question_text, difficulty, answer, explanation
            FROM questions
            WHERE topic_id = ? AND difficulty = ?
            ORDER BY question_id;
        """
        params = (topic_id, difficulty.strip())
    else:
        sql = """
            SELECT question_id, topic_id, question_text, difficulty, answer, explanation
            FROM questions
            WHERE topic_id = ?
            ORDER BY question_id;
        """
        params = (topic_id,)

    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [
            Question(
                question_id=row["question_id"],
                topic_id=row["topic_id"],
                question_text=row["question_text"],
                difficulty=row["difficulty"],
                answer=row["answer"],
                explanation=row["explanation"],
            )
            for row in rows
        ]


# =============================================================================
# 4. LEARNING SESSION FUNCTIONS
# =============================================================================

def save_learning_session(
    user_id: str,
    topic_id: str,
    started_at: Optional[str] = None,
    ended_at: Optional[str] = None,
    duration: Optional[int] = None,
    session_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> LearningSession:
    """
    Saves or records a learning session with duration validation.
    """
    if duration is not None and duration < 0:
        raise ValueError("Duration cannot be negative.")

    sid = session_id or _generate_id()
    start = started_at or _current_timestamp()

    sql = """
        INSERT INTO learning_sessions (session_id, user_id, topic_id, started_at, ended_at, duration)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            ended_at = excluded.ended_at,
            duration = excluded.duration;
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (sid, user_id, topic_id, start, ended_at, duration))

    return LearningSession(
        session_id=sid,
        user_id=user_id,
        topic_id=topic_id,
        started_at=start,
        ended_at=ended_at,
        duration=duration,
    )


def save_learning_history(
    user_id: str,
    topic_id: str,
    concept_query: str = "",
    analogy: str = "",
    level: str = "beginner",
    time_spent: int = 0,
    db_path: Optional[str] = None
) -> str:
    """Backwards-compatible helper for recording an interaction."""
    session = save_learning_session(
        user_id=user_id,
        topic_id=topic_id,
        duration=time_spent,
        db_path=db_path
    )
    return session.session_id


# =============================================================================
# 5. ATTEMPT LOGGING FUNCTIONS
# =============================================================================

def save_attempt(
    user_id: str,
    topic_id: str,
    question_id: str,
    answer: str,
    correct: bool,
    response_time: int,
    created_at: Optional[str] = None,
    attempt_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> Attempt:
    """
    Records a user's answer attempt for a question.
    """
    if response_time < 0:
        raise ValueError("response_time cannot be negative.")

    aid = attempt_id or _generate_id()
    now = created_at or _current_timestamp()
    correct_int = 1 if correct else 0

    sql = """
        INSERT INTO attempts (attempt_id, user_id, topic_id, question_id, answer, correct, response_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (aid, user_id, topic_id, question_id, answer, correct_int, response_time, now))

    return Attempt(
        attempt_id=aid,
        user_id=user_id,
        topic_id=topic_id,
        question_id=question_id,
        answer=answer,
        correct=bool(correct),
        response_time=response_time,
        created_at=now,
    )


def get_attempts_by_user(
    user_id: str,
    topic_id: Optional[str] = None,
    limit: int = 50,
    db_path: Optional[str] = None
) -> List[Attempt]:
    """
    Retrieves recent attempts by a user, optionally filtered by topic.
    """
    if topic_id:
        sql = """
            SELECT a.attempt_id, a.user_id, a.topic_id, a.question_id, a.answer,
                   a.correct, a.response_time, a.created_at,
                   q.question_text, t.topic_name
            FROM attempts a
            JOIN questions q ON a.question_id = q.question_id
            JOIN topics t ON a.topic_id = t.topic_id
            WHERE a.user_id = ? AND a.topic_id = ?
            ORDER BY a.created_at DESC
            LIMIT ?;
        """
        params = (user_id, topic_id, limit)
    else:
        sql = """
            SELECT a.attempt_id, a.user_id, a.topic_id, a.question_id, a.answer,
                   a.correct, a.response_time, a.created_at,
                   q.question_text, t.topic_name
            FROM attempts a
            JOIN questions q ON a.question_id = q.question_id
            JOIN topics t ON a.topic_id = t.topic_id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
            LIMIT ?;
        """
        params = (user_id, limit)

    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [
            Attempt(
                attempt_id=row["attempt_id"],
                user_id=row["user_id"],
                topic_id=row["topic_id"],
                question_id=row["question_id"],
                answer=row["answer"],
                correct=bool(row["correct"]),
                response_time=row["response_time"],
                created_at=str(row["created_at"]),
                question_text=row["question_text"],
                topic_name=row["topic_name"],
            )
            for row in rows
        ]


# =============================================================================
# 6. TOPIC MASTERY FUNCTIONS
# =============================================================================

def get_topic_mastery(
    user_id: str,
    topic_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> Union[Optional[TopicMastery], List[TopicMastery]]:
    """
    Retrieves mastery score and confidence.
    If topic_id is provided, returns Optional[TopicMastery].
    If topic_id is None, returns List[TopicMastery] across all topics for the user.
    """
    if topic_id:
        sql = """
            SELECT tm.user_id, tm.topic_id, tm.mastery_score, tm.confidence, tm.last_updated,
                   t.topic_name, t.subject
            FROM topic_mastery tm
            JOIN topics t ON tm.topic_id = t.topic_id
            WHERE tm.user_id = ? AND tm.topic_id = ?;
        """
        with get_db_cursor(db_path=db_path) as cursor:
            cursor.execute(sql, (user_id, topic_id))
            row = cursor.fetchone()
            if not row:
                return None
            return TopicMastery(
                user_id=row["user_id"],
                topic_id=row["topic_id"],
                mastery_score=float(row["mastery_score"]),
                confidence=float(row["confidence"]),
                last_updated=str(row["last_updated"]),
                topic_name=row["topic_name"],
                subject=row["subject"],
            )
    else:
        sql = """
            SELECT tm.user_id, tm.topic_id, tm.mastery_score, tm.confidence, tm.last_updated,
                   t.topic_name, t.subject
            FROM topic_mastery tm
            JOIN topics t ON tm.topic_id = t.topic_id
            WHERE tm.user_id = ?
            ORDER BY tm.mastery_score DESC;
        """
        with get_db_cursor(db_path=db_path) as cursor:
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            return [
                TopicMastery(
                    user_id=row["user_id"],
                    topic_id=row["topic_id"],
                    mastery_score=float(row["mastery_score"]),
                    confidence=float(row["confidence"]),
                    last_updated=str(row["last_updated"]),
                    topic_name=row["topic_name"],
                    subject=row["subject"],
                )
                for row in rows
            ]


def update_topic_mastery(
    user_id: str,
    topic_id: str,
    mastery_score: float,
    confidence: float = 0.8,
    last_updated: Optional[str] = None,
    db_path: Optional[str] = None
) -> TopicMastery:
    """
    Upserts mastery score and confidence for a user on a given topic.
    Validates that score and confidence are between 0.0 and 1.0.
    """
    if not (0.0 <= mastery_score <= 1.0):
        raise ValueError("mastery_score must be between 0.0 and 1.0.")
    if not (0.0 <= confidence <= 1.0):
        raise ValueError("confidence must be between 0.0 and 1.0.")

    now = last_updated or _current_timestamp()

    sql = """
        INSERT INTO topic_mastery (user_id, topic_id, mastery_score, confidence, last_updated)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, topic_id) DO UPDATE SET
            mastery_score = excluded.mastery_score,
            confidence = excluded.confidence,
            last_updated = excluded.last_updated;
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (user_id, topic_id, mastery_score, confidence, now))

    topic = get_topic(topic_id, db_path=db_path)
    topic_name = topic.topic_name if topic else None
    subject = topic.subject if topic else None

    return TopicMastery(
        user_id=user_id,
        topic_id=topic_id,
        mastery_score=float(mastery_score),
        confidence=float(confidence),
        last_updated=now,
        topic_name=topic_name,
        subject=subject,
    )


def update_mastery(user_id: str, topic_id: str, score_delta: float, db_path: Optional[str] = None) -> None:
    """Backwards-compatible helper to increment/decrement mastery score."""
    existing = get_topic_mastery(user_id, topic_id, db_path=db_path)
    current_score = existing.mastery_score if existing else 0.0
    new_score = max(0.0, min(1.0, current_score + score_delta))
    update_topic_mastery(user_id, topic_id, mastery_score=new_score, confidence=0.8, db_path=db_path)


# =============================================================================
# 7. FEEDBACK FUNCTIONS
# =============================================================================

def save_feedback(
    user_id: str,
    topic_id: str,
    feedback_type: str,
    created_at: Optional[str] = None,
    feedback_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> Feedback:
    """
    Records learner feedback after a concept explanation.
    feedback_type must be one of: 'got_it', 'almost', 'still_confused'
    """
    allowed_types = {"got_it", "almost", "still_confused"}
    if feedback_type not in allowed_types:
        raise ValueError(f"Invalid feedback_type '{feedback_type}'. Must be one of {allowed_types}.")

    fid = feedback_id or _generate_id()
    now = created_at or _current_timestamp()

    sql = """
        INSERT INTO feedback (feedback_id, user_id, topic_id, feedback_type, created_at)
        VALUES (?, ?, ?, ?, ?);
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (fid, user_id, topic_id, feedback_type, now))

    topic = get_topic(topic_id, db_path=db_path)
    topic_name = topic.topic_name if topic else None

    return Feedback(
        feedback_id=fid,
        user_id=user_id,
        topic_id=topic_id,
        feedback_type=feedback_type,
        created_at=now,
        topic_name=topic_name,
    )


def get_feedback_by_user(
    user_id: str,
    topic_id: Optional[str] = None,
    limit: int = 50,
    db_path: Optional[str] = None
) -> List[Feedback]:
    """
    Retrieves feedback history for a user, optionally filtered by topic.
    """
    if topic_id:
        sql = """
            SELECT f.feedback_id, f.user_id, f.topic_id, f.feedback_type, f.created_at, t.topic_name
            FROM feedback f
            JOIN topics t ON f.topic_id = t.topic_id
            WHERE f.user_id = ? AND f.topic_id = ?
            ORDER BY f.created_at DESC
            LIMIT ?;
        """
        params = (user_id, topic_id, limit)
    else:
        sql = """
            SELECT f.feedback_id, f.user_id, f.topic_id, f.feedback_type, f.created_at, t.topic_name
            FROM feedback f
            JOIN topics t ON f.topic_id = t.topic_id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
            LIMIT ?;
        """
        params = (user_id, limit)

    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [
            Feedback(
                feedback_id=row["feedback_id"],
                user_id=row["user_id"],
                topic_id=row["topic_id"],
                feedback_type=row["feedback_type"],
                created_at=str(row["created_at"]),
                topic_name=row["topic_name"],
            )
            for row in rows
        ]


# =============================================================================
# 8. RECOMMENDATION FUNCTIONS
# =============================================================================

def save_recommendation(
    user_id: str,
    topic_id: str,
    recommendation_type: str,
    reason: str,
    completed: bool = False,
    created_at: Optional[str] = None,
    recommendation_id: Optional[str] = None,
    db_path: Optional[str] = None
) -> Recommendation:
    """
    Saves an AI-generated learning recommendation for a user.
    """
    rid = recommendation_id or _generate_id()
    now = created_at or _current_timestamp()
    comp_int = 1 if completed else 0

    sql = """
        INSERT INTO recommendations (
            recommendation_id, user_id, topic_id, recommendation_type, reason, created_at, completed
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (rid, user_id, topic_id, recommendation_type.strip(), reason.strip(), now, comp_int))

    topic = get_topic(topic_id, db_path=db_path)
    topic_name = topic.topic_name if topic else None

    return Recommendation(
        recommendation_id=rid,
        user_id=user_id,
        topic_id=topic_id,
        recommendation_type=recommendation_type.strip(),
        reason=reason.strip(),
        created_at=now,
        completed=bool(completed),
        topic_name=topic_name,
    )


def get_recommendations(
    user_id: str,
    pending_only: bool = False,
    db_path: Optional[str] = None
) -> List[Recommendation]:
    """
    Retrieves recommendations for a user. If pending_only=True, returns only uncompleted ones.
    """
    if pending_only:
        sql = """
            SELECT r.recommendation_id, r.user_id, r.topic_id, r.recommendation_type,
                   r.reason, r.created_at, r.completed, t.topic_name
            FROM recommendations r
            JOIN topics t ON r.topic_id = t.topic_id
            WHERE r.user_id = ? AND r.completed = 0
            ORDER BY r.created_at DESC;
        """
    else:
        sql = """
            SELECT r.recommendation_id, r.user_id, r.topic_id, r.recommendation_type,
                   r.reason, r.created_at, r.completed, t.topic_name
            FROM recommendations r
            JOIN topics t ON r.topic_id = t.topic_id
            WHERE r.user_id = ?
            ORDER BY r.completed ASC, r.created_at DESC;
        """

    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        return [
            Recommendation(
                recommendation_id=row["recommendation_id"],
                user_id=row["user_id"],
                topic_id=row["topic_id"],
                recommendation_type=row["recommendation_type"],
                reason=row["reason"],
                created_at=str(row["created_at"]),
                completed=bool(row["completed"]),
                topic_name=row["topic_name"],
            )
            for row in rows
        ]


def mark_recommendation_completed(recommendation_id: str, db_path: Optional[str] = None) -> bool:
    """
    Marks a recommendation as completed. Returns True if updated, False if not found.
    """
    sql = "UPDATE recommendations SET completed = 1 WHERE recommendation_id = ?;"
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (recommendation_id,))
        return cursor.rowcount > 0


# =============================================================================
# 9. REFRESH SESSION FUNCTIONS (Smart Refresh)
# =============================================================================

def save_refresh_session(
    user_id: str,
    activity_type: str,
    started_at: Optional[str] = None,
    ended_at: Optional[str] = None,
    duration: Optional[int] = None,
    completed: bool = False,
    refresh_id: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    db_path: Optional[str] = None
) -> RefreshSession:
    """
    Saves a Smart Refresh spaced repetition session.
    Validates that duration >= 0.
    """
    final_dur = duration if duration is not None else duration_seconds
    if final_dur is not None and final_dur < 0:
        raise ValueError("Duration cannot be negative.")

    rid = refresh_id or _generate_id()
    start = started_at or _current_timestamp()
    comp_int = 1 if completed else 0

    sql = """
        INSERT INTO refresh_sessions (
            refresh_id, user_id, activity_type, started_at, ended_at, duration, completed
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(refresh_id) DO UPDATE SET
            ended_at = excluded.ended_at,
            duration = excluded.duration,
            completed = excluded.completed;
    """
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(sql, (rid, user_id, activity_type.strip(), start, ended_at, final_dur, comp_int))

    return RefreshSession(
        refresh_id=rid,
        user_id=user_id,
        activity_type=activity_type.strip(),
        started_at=start,
        ended_at=ended_at,
        duration=final_dur,
        completed=bool(completed),
    )


def log_smart_refresh(user_id: str, activity_type: str, duration_seconds: int, db_path: Optional[str] = None) -> str:
    """Backwards-compatible helper to log smart refresh activity."""
    session = save_refresh_session(
        user_id=user_id,
        activity_type=activity_type,
        duration=duration_seconds,
        completed=True,
        db_path=db_path
    )
    return session.refresh_id


def get_refresh_sessions_by_user(
    user_id: str,
    limit: int = 50,
    db_path: Optional[str] = None
) -> List[RefreshSession]:
    """
    Retrieves Smart Refresh history for a user.
    """
    sql = """
        SELECT refresh_id, user_id, activity_type, started_at, ended_at, duration, completed
        FROM refresh_sessions
        WHERE user_id = ?
        ORDER BY started_at DESC
        LIMIT ?;
    """
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sql, (user_id, limit))
        rows = cursor.fetchall()
        return [
            RefreshSession(
                refresh_id=row["refresh_id"],
                user_id=row["user_id"],
                activity_type=row["activity_type"],
                started_at=str(row["started_at"]),
                ended_at=str(row["ended_at"]) if row["ended_at"] else None,
                duration=row["duration"],
                completed=bool(row["completed"]),
            )
            for row in rows
        ]


# =============================================================================
# 10. RECENT LEARNING HISTORY AGGREGATION
# =============================================================================

def get_recent_learning_history(user_id: str, limit: int = 20, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Aggregates learning history for a user across sessions, attempts, feedback,
    and refresh sessions for personalized progress tracking.
    """
    # 1. Recent learning sessions
    sessions_sql = """
        SELECT ls.session_id, ls.started_at, ls.ended_at, ls.duration, t.topic_name, t.subject
        FROM learning_sessions ls
        JOIN topics t ON ls.topic_id = t.topic_id
        WHERE ls.user_id = ?
        ORDER BY ls.started_at DESC
        LIMIT ?;
    """

    # 2. Attempt metrics
    attempt_metrics_sql = """
        SELECT 
            COUNT(*) as total_attempts,
            SUM(correct) as correct_attempts,
            AVG(response_time) as avg_response_time
        FROM attempts
        WHERE user_id = ?;
    """

    # 3. Recent attempts
    recent_attempts_sql = """
        SELECT a.attempt_id, a.answer, a.correct, a.response_time, a.created_at,
               q.question_text, t.topic_name
        FROM attempts a
        JOIN questions q ON a.question_id = q.question_id
        JOIN topics t ON a.topic_id = t.topic_id
        WHERE a.user_id = ?
        ORDER BY a.created_at DESC
        LIMIT ?;
    """

    # 4. Feedback breakdown
    feedback_sql = """
        SELECT feedback_type, COUNT(*) as count
        FROM feedback
        WHERE user_id = ?
        GROUP BY feedback_type;
    """

    # 5. Smart Refresh summary
    refresh_sql = """
        SELECT refresh_id, activity_type, started_at, duration, completed
        FROM refresh_sessions
        WHERE user_id = ?
        ORDER BY started_at DESC
        LIMIT ?;
    """

    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(sessions_sql, (user_id, limit))
        sessions = [dict(row) for row in cursor.fetchall()]

        cursor.execute(attempt_metrics_sql, (user_id,))
        metrics_row = cursor.fetchone()
        total_att = metrics_row["total_attempts"] if metrics_row else 0
        corr_att = metrics_row["correct_attempts"] if metrics_row and metrics_row["correct_attempts"] else 0
        avg_rt = metrics_row["avg_response_time"] if metrics_row and metrics_row["avg_response_time"] else 0.0
        accuracy = (corr_att / total_att * 100.0) if total_att > 0 else 0.0

        cursor.execute(recent_attempts_sql, (user_id, limit))
        recent_attempts = [
            {
                "attempt_id": r["attempt_id"],
                "answer": r["answer"],
                "correct": bool(r["correct"]),
                "response_time": r["response_time"],
                "created_at": str(r["created_at"]),
                "question_text": r["question_text"],
                "topic_name": r["topic_name"],
            }
            for r in cursor.fetchall()
        ]

        cursor.execute(feedback_sql, (user_id,))
        feedback_distribution = {row["feedback_type"]: row["count"] for row in cursor.fetchall()}

        cursor.execute(refresh_sql, (user_id, limit))
        refresh_sessions = [
            {
                "refresh_id": r["refresh_id"],
                "activity_type": r["activity_type"],
                "started_at": str(r["started_at"]),
                "duration": r["duration"],
                "completed": bool(r["completed"]),
            }
            for r in cursor.fetchall()
        ]

    # Topic mastery snapshot
    mastery_list = get_topic_mastery(user_id, db_path=db_path)
    if isinstance(mastery_list, list):
        mastery_summary = [m.to_dict() for m in mastery_list]
    else:
        mastery_summary = []

    return {
        "user_id": user_id,
        "recent_learning_sessions": sessions,
        "recent_attempts": recent_attempts,
        "attempt_stats": {
            "total_attempts": total_att,
            "correct_attempts": corr_att,
            "accuracy_percent": round(accuracy, 2),
            "avg_response_time": round(avg_rt, 2) if avg_rt else 0.0,
        },
        "feedback_distribution": feedback_distribution,
        "recent_refresh_sessions": refresh_sessions,
        "topic_mastery_overview": mastery_summary,
    }

def get_all_users(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all users in the system."""
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute("SELECT * FROM users ORDER BY name ASC")
        rows = cursor.fetchall()
        users = []
        for r in rows:
            u = dict(r)
            u["username"] = r["name"]
            users.append(u)
        return users

def get_all_topics(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all topics in the database."""
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute("SELECT * FROM topics ORDER BY topic_name ASC")
        rows = cursor.fetchall()
        topics = []
        for r in rows:
            t = dict(r)
            t["title"] = r["topic_name"]
            t["category"] = r["subject"]
            topics.append(t)
        return topics

def get_db_learner_profile(user_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve learner profile for a specific user."""
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute("SELECT * FROM learner_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        p = dict(row)
        p["estimated_level"] = row["preferred_level"]
        p["preferred_learning_style"] = row["learning_preference"]
        return p

def update_db_learner_profile(user_id: str, level: str, style: str, db_path: Optional[str] = None) -> None:
    """Update user learning level and style in database."""
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(
            """
            UPDATE learner_profiles 
            SET preferred_level = ?, learning_preference = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (level, style, user_id)
        )

def get_learning_history(user_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve explanation history with titles for a user."""
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(
            """
            SELECT ls.*, t.topic_name as title 
            FROM learning_sessions ls 
            JOIN topics t ON ls.topic_id = t.topic_id 
            WHERE ls.user_id = ? 
            ORDER BY ls.started_at DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        history = []
        for r in rows:
            h = dict(r)
            h["title"] = r["title"]
            h["explanation_level"] = "beginner"
            h["created_at"] = str(r["started_at"])
            h["time_spent_seconds"] = r["duration"] or 0
            history.append(h)
        return history

def get_smart_refresh_history(user_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve break logs for a user."""
    with get_db_cursor(db_path=db_path) as cursor:
        cursor.execute(
            "SELECT * FROM refresh_sessions WHERE user_id = ? ORDER BY started_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        history = []
        for r in rows:
            h = dict(r)
            h["duration_seconds"] = r["duration"] or 0
            h["created_at"] = str(r["started_at"])
            history.append(h)
        return history

def create_topic_if_not_exists(topic_id: str, title: str, category: str, db_path: Optional[str] = None) -> None:
    """Inserts a new topic if it does not already exist."""
    with get_db_cursor(commit=True, db_path=db_path) as cursor:
        cursor.execute(
            "INSERT OR IGNORE INTO topics (topic_id, topic_name, subject, difficulty) VALUES (?, ?, ?, 'beginner')",
            (topic_id, title, category)
        )

