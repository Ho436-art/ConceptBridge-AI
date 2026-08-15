"""
Data Schemas and Dataclasses for ConceptBridge AI.
Provides typed, serializable contracts across AI, UI, Database, and Refresh modules.
Supports both object attribute access (obj.concept) and dict access (obj['concept']).
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum


class DictAccessibleMixin:
    """Provides dictionary-like subscript access obj['key'] and 'key' in obj."""
    def __getitem__(self, item: str) -> Any:
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)


class LearnerLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    UNDETERMINED = "undetermined"
    LET_AI_DETERMINE = "let_ai_determine"


class ExplanationStyle(str, Enum):
    ANALOGY_FIRST = "analogy_first"
    SUPER_SIMPLE = "super_simple"
    STEP_BY_STEP = "step_by_step"
    VISUAL = "visual"
    PRACTICAL_CODE = "practical_code"
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"


class FeedbackType(str, Enum):
    GOT_IT = "got_it"
    ALMOST = "almost"
    STILL_CONFUSED = "still_confused"


@dataclass
class UnderstandingCheck(DictAccessibleMixin):
    """Micro-quiz question embedded with each concept explanation."""
    question: str
    options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    explanation: str = ""
    concept_tested: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConceptExplanation(DictAccessibleMixin):
    """Structured response from the AI Teaching Engine."""
    concept: str
    real_world_analogy: str
    simple_explanation: str
    technical_explanation: str
    practical_application: str
    example_code_or_visual: str
    understanding_check: UnderstandingCheck
    difficulty: str = "beginner"
    confidence: float = 0.85
    style_used: str = "analogy_first"
    key_takeaways: List[str] = field(default_factory=list)
    diagram_type: str = "none"  # 'graphviz', 'mermaid', 'none'
    diagram_code: Optional[str] = None
    diagram_caption: str = ""

    # Backward compatibility aliases for property names
    @property
    def analogy(self) -> str:
        return self.real_world_analogy

    @property
    def beginner_explanation(self) -> str:
        return self.simple_explanation

    @property
    def practical_example(self) -> str:
        return self.practical_application

    @property
    def visual_explanation(self) -> str:
        return self.example_code_or_visual

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if isinstance(self.understanding_check, UnderstandingCheck):
            data["understanding_check"] = self.understanding_check.to_dict()
        # Include aliases in dictionary output
        data["analogy"] = self.real_world_analogy
        data["beginner_explanation"] = self.simple_explanation
        data["practical_example"] = self.practical_application
        data["visual_explanation"] = self.example_code_or_visual
        return data


@dataclass
class TopicMastery(DictAccessibleMixin):
    """Granular mastery metrics for an individual topic."""
    topic: str
    score: float = 0.0              # Range: 0.0 to 1.0
    confidence: float = 0.5         # Confidence in the estimate (0.0 to 1.0)
    attempts_count: int = 0
    correct_count: int = 0
    status: str = "not_started"     # not_started, struggling, learning, mastered, needs_revision
    last_reviewed: str = ""
    misconceptions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LearnerProfile(DictAccessibleMixin):
    """Comprehensive, dynamic profile built incrementally across interactions."""
    user_id: str
    onboarded_level: str = "let_ai_determine"
    estimated_level: str = "undetermined"
    level_confidence: float = 0.3
    preferred_style: str = "analogy_first"
    topic_mastery: Dict[str, TopicMastery] = field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)
    weak_topics: List[str] = field(default_factory=list)
    total_interactions: int = 0
    streak_correct: int = 0
    streak_incorrect: int = 0
    style_effectiveness: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["topic_mastery"] = {
            k: v.to_dict() if isinstance(v, TopicMastery) else v
            for k, v in self.topic_mastery.items()
        }
        return res


@dataclass
class MisconceptionResult(DictAccessibleMixin):
    """Result from the misconception detection engine."""
    concept: str
    has_misconception: bool
    identified_misconception: Optional[str] = None
    explanation: Optional[str] = None
    recommended_correction: Optional[str] = None
    confidence: float = 0.0
    underlying_category: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecommendationResult(DictAccessibleMixin):
    """Personalized learning pathway recommendation."""
    current_topic: Optional[str]
    suggested_next_topic: str
    recommended_difficulty: str
    reason: str
    weak_topics_to_review: List[str] = field(default_factory=list)
    prerequisites_to_revisit: List[str] = field(default_factory=list)
    confidence: float = 0.85

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RefreshDecision(DictAccessibleMixin):
    """Recommendation payload for the Smart Refresh break feature."""
    recommend_break: bool
    fatigue_score: float                # 0.0 to 1.0 estimated cognitive fatigue
    reasons: List[str] = field(default_factory=list)
    cooldown_active: bool = False
    cooldown_remaining_minutes: float = 0.0
    suggested_activity: Optional[str] = None
    can_manual_request: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RefreshSession(DictAccessibleMixin):
    """Active Smart Refresh session checkpoint."""
    session_id: str
    user_id: str
    activity_type: str
    max_duration_seconds: int = 300     # 5-minute strict cap
    is_completed: bool = False
    resume_concept: Optional[str] = None
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
