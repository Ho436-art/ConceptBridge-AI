"""
Data Schemas and Dataclasses
Provides common data structures across AI, UI, Database, and Refresh modules.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class LearnerProfile:
    user_id: str
    estimated_level: str = "beginner"
    topic_mastery: Dict[str, float] = field(default_factory=dict)
    interaction_count: int = 0
    weak_topics: List[str] = field(default_factory=list)

@dataclass
class ConceptExplanation:
    concept: str
    analogy: str
    beginner_explanation: str
    technical_explanation: str
    practical_example: str
    visual_explanation: Optional[str] = None
    targeted_level: str = "beginner"

@dataclass
class RefreshSession:
    session_id: str
    user_id: str
    activity_type: str
    max_duration_seconds: int = 300
    is_completed: bool = False
    resume_concept: Optional[str] = None
