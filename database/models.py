"""
ConceptBridge AI - Data Models
Type-safe dataclasses for all core database entities with dictionary conversion helpers.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class User:
    """User account entity."""
    user_id: str
    name: str
    email: str
    created_at: str
    password_hash: Optional[str] = None

    def __str__(self) -> str:
        return self.user_id

    def __getitem__(self, item: str) -> Any:
        return self.to_dict(include_sensitive=True).get(item)

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary, omitting password_hash by default."""
        data = asdict(self)
        if not include_sensitive:
            data.pop("password_hash", None)
        # Compatibility aliases
        data["username"] = self.name
        return data


@dataclass
class LearnerProfile:
    """Personalized learner profile."""
    profile_id: str
    user_id: str
    preferred_level: str
    learning_preference: str
    overall_level: str
    created_at: str
    updated_at: str

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["estimated_level"] = self.preferred_level
        data["preferred_learning_style"] = self.learning_preference
        return data


@dataclass
class Topic:
    """Learning topic entity."""
    topic_id: str
    topic_name: str
    subject: str
    difficulty: str
    description: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["title"] = self.topic_name
        data["category"] = self.subject
        return data


@dataclass
class Question:
    """Question assessment entity."""
    question_id: str
    topic_id: str
    question_text: str
    difficulty: str
    answer: str
    explanation: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LearningSession:
    """Learning session tracking entity."""
    session_id: str
    user_id: str
    topic_id: str
    started_at: str
    ended_at: Optional[str] = None
    duration: Optional[int] = None
    topic_name: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Attempt:
    """Question attempt log entity."""
    attempt_id: str
    user_id: str
    topic_id: str
    question_id: str
    answer: str
    correct: bool
    response_time: int  # in milliseconds or seconds
    created_at: str
    question_text: Optional[str] = None
    topic_name: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TopicMastery:
    """Topic mastery score & confidence tracker."""
    user_id: str
    topic_id: str
    mastery_score: float  # 0.0 to 1.0
    confidence: float     # 0.0 to 1.0
    last_updated: str
    topic_name: Optional[str] = None
    subject: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["title"] = self.topic_name
        data["category"] = self.subject
        return data
        return asdict(self)


@dataclass
class Feedback:
    """Subjective learner feedback."""
    feedback_id: str
    user_id: str
    topic_id: str
    feedback_type: str  # 'got_it', 'almost', 'still_confused'
    created_at: str
    topic_name: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Recommendation:
    """AI-generated next-step recommendation."""
    recommendation_id: str
    user_id: str
    topic_id: str
    recommendation_type: str
    reason: str
    created_at: str
    completed: bool = False
    topic_name: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RefreshSession:
    """Smart Refresh spaced repetition session."""
    refresh_id: str
    user_id: str
    activity_type: str
    started_at: str
    ended_at: Optional[str] = None
    duration: Optional[int] = None
    completed: bool = False

    def __getitem__(self, item: str) -> Any:
        return self.to_dict().get(item)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
