-- =============================================================================
-- ConceptBridge AI - Database Schema
-- Owner: Member 3 (Database)
-- Database engine: SQLite (portable for local dev/hackathon)
-- =============================================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Learner Profiles Table
CREATE TABLE IF NOT EXISTS learner_profiles (
    profile_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    estimated_level TEXT DEFAULT 'beginner', -- beginner, intermediate, advanced
    interaction_count INTEGER DEFAULT 0,
    preferred_learning_style TEXT DEFAULT 'analogical',
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Topics Table
CREATE TABLE IF NOT EXISTS topics (
    topic_id TEXT PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    difficulty_level TEXT DEFAULT 'beginner',
    prerequisites TEXT, -- JSON or comma-separated topic IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Learning History Table
CREATE TABLE IF NOT EXISTS learning_history (
    history_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    concept_query TEXT NOT NULL,
    analogy_presented TEXT,
    explanation_level TEXT,
    time_spent_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

-- 5. Questions Table
CREATE TABLE IF NOT EXISTS questions (
    question_id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    options_json TEXT, -- JSON array of choices
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    difficulty TEXT DEFAULT 'medium',
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

-- 6. Attempts Table
CREATE TABLE IF NOT EXISTS attempts (
    attempt_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    misconception_detected TEXT,
    attempt_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
);

-- 7. Topic Mastery Table
CREATE TABLE IF NOT EXISTS topic_mastery (
    mastery_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    mastery_score REAL DEFAULT 0.0, -- Range 0.0 to 1.0
    status TEXT DEFAULT 'learning', -- 'not_started', 'learning', 'mastered', 'needs_review'
    last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    UNIQUE(user_id, topic_id)
);

-- 8. Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    history_id TEXT,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    feedback_type TEXT, -- 'clarity', 'analogy_helpful', 'too_complex', etc.
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (history_id) REFERENCES learning_history(history_id) ON DELETE SET NULL
);

-- 9. Smart Refresh History Table
CREATE TABLE IF NOT EXISTS smart_refresh_history (
    refresh_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    activity_type TEXT NOT NULL, -- 'memory_game', 'riddles', 'gk', 'math', 'relaxation', etc.
    duration_seconds INTEGER NOT NULL CHECK(duration_seconds <= 300), -- max 5 mins (300 sec)
    resumed_learning_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
