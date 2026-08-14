"""
AI Teaching & Personalization Module for ConceptBridge AI.
"""

from .teaching_engine import explain_concept
from .learner_profile import get_learner_profile, update_learner_profile
from .misconception import detect_misconceptions
from .recommendations import get_next_recommendations

__all__ = [
    "explain_concept",
    "get_learner_profile",
    "update_learner_profile",
    "detect_misconceptions",
    "get_next_recommendations",
]
