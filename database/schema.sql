-- =============================================================================
-- ConceptBridge AI - Database Schema DDL
-- "From 'I don't understand' to 'Oh, it's that easy!'"
-- Compatible with SQLite (default) and MySQL / MariaDB.
-- =============================================================================

-- Enable foreign keys for SQLite sessions (handled in connection layer as well)
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- 1. USERS
-- Stores core user accounts with salted password hashes (no plaintext passwords).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. LEARNER PROFILES
-- Stores personalized learning preferences and overall level for each user.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learner_profiles (
    profile_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    preferred_level VARCHAR(50) NOT NULL DEFAULT 'beginner',
    learning_preference VARCHAR(50) NOT NULL DEFAULT 'step_by_step',
    overall_level VARCHAR(50) NOT NULL DEFAULT 'novice',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- 3. TOPICS
-- Curated or generated educational topics categorized by subject & difficulty.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS topics (
    topic_id VARCHAR(36) PRIMARY KEY,
    topic_name VARCHAR(150) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) NOT NULL DEFAULT 'beginner',
    description TEXT
);

-- -----------------------------------------------------------------------------
-- 4. QUESTIONS
-- Assessment and checkpoint questions tied to specific topics.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS questions (
    question_id VARCHAR(36) PRIMARY KEY,
    topic_id VARCHAR(36) NOT NULL,
    question_text TEXT NOT NULL,
    difficulty VARCHAR(50) NOT NULL DEFAULT 'beginner',
    answer TEXT NOT NULL,
    explanation TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- 5. LEARNING SESSIONS
-- Tracks active learning interactions, start/end timestamps, and duration.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    topic_id VARCHAR(36) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration INTEGER CHECK (duration IS NULL OR duration >= 0),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- 6. ATTEMPTS
-- Granular log of user question responses, correctness, and response times.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attempts (
    attempt_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    topic_id VARCHAR(36) NOT NULL,
    question_id VARCHAR(36) NOT NULL,
    answer TEXT NOT NULL,
    correct INTEGER NOT NULL CHECK (correct IN (0, 1)),
    response_time INTEGER NOT NULL CHECK (response_time >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE RESTRICT,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- 7. TOPIC MASTERY
-- Continuous tracking of user mastery scores and model confidence per topic.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS topic_mastery (
    user_id VARCHAR(36) NOT NULL,
    topic_id VARCHAR(36) NOT NULL,
    mastery_score REAL NOT NULL CHECK (mastery_score >= 0.0 AND mastery_score <= 1.0),
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, topic_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- 8. FEEDBACK
-- Captures subjective learner feedback after concept explanations.
-- feedback_type constrained to: 'got_it', 'almost', 'still_confused'
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    topic_id VARCHAR(36) NOT NULL,
    feedback_type VARCHAR(50) NOT NULL CHECK (feedback_type IN ('got_it', 'almost', 'still_confused')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- 9. RECOMMENDATIONS
-- Recommended next actions generated by the AI learning engine.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    topic_id VARCHAR(36) NOT NULL,
    recommendation_type VARCHAR(100) NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- 10. REFRESH SESSIONS
-- Tracks Smart Refresh sessions for spaced repetition and memory retention.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS refresh_sessions (
    refresh_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration INTEGER CHECK (duration IS NULL OR duration >= 0),
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_learner_profiles_user ON learner_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_user ON learning_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_topic ON learning_sessions(topic_id);
CREATE INDEX IF NOT EXISTS idx_attempts_user_topic ON attempts(user_id, topic_id);
CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_topic_mastery_user ON topic_mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_completed ON recommendations(user_id, completed);
CREATE INDEX IF NOT EXISTS idx_refresh_sessions_user ON refresh_sessions(user_id);
