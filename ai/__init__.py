"""
AI Core Subsystem for ConceptBridge AI.
Owner: Member 1 (Team Lead / AI & ML)

Exposes standard, decoupled interfaces for the AI Teaching Engine,
Conversational Intent Routing, Dynamic Learner Profiling, Misconception Detection,
Personalized Recommendations, and the Smart Refresh Decision Engine.
"""

from .teaching_engine import explain_concept
from .feedback_handler import process_feedback
from .learner_profile import (
    LearnerProfileManager,
    get_learner_profile,
    update_learner_profile,
    update_mastery,
)
from .misconception import detect_misconceptions
from .recommendations import (
    get_learning_recommendation,
    get_next_recommendations,
)
from .refresh_decision import (
    should_offer_refresh,
    request_manual_refresh,
    calculate_fatigue_score,
)
from .conversation_engine import handle_chat_message, classify_intent
from .diagram_generator import get_diagram_for_concept
from .verified_knowledge import lookup_verified_knowledge

__all__ = [
    "explain_concept",
    "process_feedback",
    "LearnerProfileManager",
    "get_learner_profile",
    "update_learner_profile",
    "update_mastery",
    "detect_misconceptions",
    "get_learning_recommendation",
    "get_next_recommendations",
    "should_offer_refresh",
    "request_manual_refresh",
    "calculate_fatigue_score",
    "handle_chat_message",
    "classify_intent",
    "get_diagram_for_concept",
    "lookup_verified_knowledge",
]
