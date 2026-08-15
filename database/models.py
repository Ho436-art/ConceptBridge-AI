"""
ConceptBridge AI - Data Models
Type-safe dataclasses for all core database entities with dictionary conversion helpers.
Includes DictAccessibleMixin to seamlessly support both object attribute access (obj.prop)
and dictionary-style access (obj['prop'], obj.get('prop', default)).
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List


class DictAccessibleMixin:
    """Provides dictionary-like subscript access obj['key'], obj.get('key', default), and 'key' in obj."""
    def __getitem__(self, item: str) -> Any:
        val = self.to_dict().get(item)
        if val is None and hasattr(self, item):
            val = getattr(self, item)
        return val

    def get(self, item: str, default: Any = None) -> Any:
        res = self.to_dict().get(item)
        if res is not None:
            return res
        return getattr(self, item, default)

    def __contains__(self, item: str) -> bool:
        return item in self.to_dict() or hasattr(self, item)

    def keys(self):
        return self.to_dict().keys()

    def items(self):
        return self.to_dict().items()

    def values(self):
        return self.to_dict().values()


@dataclass
class User(DictAccessibleMixin):
    """User account entity."""
    user_id: str
    name: str
    email: str
    created_at: str
    password_hash: Optional[str] = None

    def __str__(self) -> str:
        return self.user_id

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary, omitting password_hash by default."""
        data = asdict(self)
        if not include_sensitive:
            data.pop("password_hash", None)
        # Compatibility aliases
        data["username"] = self.name
        return data


@dataclass
class LearnerProfile(DictAccessibleMixin):
    """Personalized learner profile."""
    profile_id: str
    user_id: str
    preferred_level: str
    learning_preference: str
    overall_level: str
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["estimated_level"] = self.preferred_level
        data["preferred_learning_style"] = self.learning_preference
        return data


@dataclass
class Topic(DictAccessibleMixin):
    """Learning topic entity."""
    topic_id: str
    topic_name: str
    subject: str
    difficulty: str
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["title"] = self.topic_name
        data["category"] = self.subject
        return data


@dataclass
class Question(DictAccessibleMixin):
    """Question assessment entity."""
    question_id: str
    topic_id: str
    question_text: str
    difficulty: str
    answer: str
    explanation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LearningSession(DictAccessibleMixin):
    """Learning session tracking entity."""
    session_id: str
    user_id: str
    topic_id: str
    started_at: str
    ended_at: Optional[str] = None
    duration: Optional[int] = None
    topic_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Attempt(DictAccessibleMixin):
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TopicMastery(DictAccessibleMixin):
    """Topic mastery score & confidence tracker."""
    user_id: str
    topic_id: str
    mastery_score: float  # 0.0 to 1.0
    confidence: float     # 0.0 to 1.0
    last_updated: str
    topic_name: Optional[str] = None
    subject: Optional[str] = None
    status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["title"] = self.topic_name or self.topic_id
        data["category"] = self.subject or "Computer Science"
        if not self.status:
            if self.mastery_score >= 0.75:
                data["status"] = "mastered"
            elif self.mastery_score < 0.40:
                data["status"] = "struggling"
            else:
                data["status"] = "learning"
        else:
            data["status"] = self.status
        return data


@dataclass
class Feedback(DictAccessibleMixin):
    """Subjective learner feedback."""
    feedback_id: str
    user_id: str
    topic_id: str
    feedback_type: str  # 'got_it', 'almost', 'still_confused'
    created_at: str
    topic_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Recommendation(DictAccessibleMixin):
    """Personalized learning recommendation."""
    recommendation_id: str
    user_id: str
    topic_id: str
    recommendation_type: str
    reason: str
    created_at: str
    topic_name: Optional[str] = None
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RefreshSession(DictAccessibleMixin):
    """Smart Refresh activity log."""
    refresh_id: str
    user_id: str
    activity_type: str
    started_at: str
    ended_at: Optional[str] = None
    duration: Optional[int] = None
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
