"""
Learner Profile and Dynamic Mastery Engine
Owner: Member 1 (Team Lead / AI & ML)

Responsibilities:
- Incremental learner profiling across interactions without single-prompt stereotyping.
- Dynamic topic mastery calculation (Bayesian / weighted moving average).
- Dynamic knowledge level estimation (Beginner -> Intermediate -> Advanced).
- Tracking feedback patterns, style effectiveness, and struggle points.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from models.schemas import (
    LearnerProfile,
    TopicMastery,
    LearnerLevel,
    ExplanationStyle,
    FeedbackType
)

# In-memory session cache (can be persisted by Member 3 via SQLite)
_PROFILE_CACHE: Dict[str, LearnerProfile] = {}


class LearnerProfileManager:
    """Manages creation, evaluation, and dynamic updates of learner profiles."""

    @staticmethod
    def create_profile(
        user_id: str,
        onboarded_level: str = "let_ai_determine",
        preferred_style: str = "analogy_first"
    ) -> LearnerProfile:
        """Create and initialize a new learner profile."""
        profile = LearnerProfile(
            user_id=user_id,
            onboarded_level=onboarded_level.lower(),
            estimated_level="undetermined" if onboarded_level == "let_ai_determine" else onboarded_level.lower(),
            level_confidence=0.3 if onboarded_level == "let_ai_determine" else 0.5,
            preferred_style=preferred_style,
            topic_mastery={},
            interaction_history=[],
            feedback_history=[],
            weak_topics=[],
            total_interactions=0,
            streak_correct=0,
            streak_incorrect=0,
            style_effectiveness={}
        )
        _PROFILE_CACHE[user_id] = profile
        return profile

    @staticmethod
    def get_or_create_profile(user_id: str) -> LearnerProfile:
        """Retrieve existing profile or create a fresh default profile."""
        if user_id not in _PROFILE_CACHE:
            return LearnerProfileManager.create_profile(user_id)
        return _PROFILE_CACHE[user_id]

    @staticmethod
    def update_mastery(
        profile: LearnerProfile,
        topic: str,
        is_correct: bool,
        difficulty: str = "beginner",
        response_time_seconds: Optional[float] = None
    ) -> TopicMastery:
        """
        Updates topic mastery using weighted Bayesian performance estimation.
        
        Args:
            profile: Target learner profile
            topic: Concept/topic name
            is_correct: Whether check-question was answered correctly
            difficulty: Difficulty level of the question ('beginner', 'intermediate', 'advanced')
            response_time_seconds: Time taken to answer
        """
        topic_key = topic.strip().lower()
        if topic_key not in profile.topic_mastery:
            profile.topic_mastery[topic_key] = TopicMastery(
                topic=topic.strip().title(),
                score=0.5,  # neutral prior
                confidence=0.3,
                attempts_count=0,
                correct_count=0,
                status="learning",
                last_reviewed=datetime.now().isoformat()
            )

        mastery = profile.topic_mastery[topic_key]
        mastery.attempts_count += 1
        mastery.last_reviewed = datetime.now().isoformat()

        # Weight scale by difficulty
        diff_weight = {"beginner": 0.08, "intermediate": 0.12, "advanced": 0.16}.get(difficulty.lower(), 0.10)

        if is_correct:
            mastery.correct_count += 1
            profile.streak_correct += 1
            profile.streak_incorrect = 0
            # Increase mastery score towards 1.0
            delta = diff_weight * (1.0 - mastery.score)
            mastery.score = min(1.0, mastery.score + delta)
        else:
            profile.streak_incorrect += 1
            profile.streak_correct = 0
            # Decrease mastery score towards 0.0
            delta = diff_weight * mastery.score * 1.2
            mastery.score = max(0.0, mastery.score - delta)

        # Update confidence (increases with number of attempts)
        mastery.confidence = min(0.95, 0.3 + (mastery.attempts_count * 0.12))

        # Classify status
        if mastery.score >= 0.80 and mastery.attempts_count >= 2:
            mastery.status = "mastered"
        elif mastery.score < 0.40 and mastery.attempts_count >= 2:
            mastery.status = "struggling"
        else:
            mastery.status = "learning"

        # Refresh weak topics list
        LearnerProfileManager._sync_weak_topics(profile)
        # Recalibrate overall knowledge level
        LearnerProfileManager.estimate_knowledge_level(profile)

        return mastery

    @staticmethod
    def record_feedback(
        profile: LearnerProfile,
        feedback_type: str,
        concept: str,
        style_used: str = "analogy_first"
    ) -> None:
        """
        Records student feedback (got_it, almost, still_confused) and updates style effectiveness.
        """
        profile.feedback_history.append({
            "concept": concept,
            "feedback_type": feedback_type,
            "style_used": style_used,
            "timestamp": datetime.now().isoformat()
        })

        if style_used not in profile.style_effectiveness:
            profile.style_effectiveness[style_used] = {"got_it": 0, "almost": 0, "still_confused": 0}

        clean_type = feedback_type.lower()
        if clean_type in profile.style_effectiveness[style_used]:
            profile.style_effectiveness[style_used][clean_type] += 1

        # If user is repeatedly confused on a topic, flag it as weak
        topic_key = concept.strip().lower()
        if clean_type == "still_confused":
            if topic_key in profile.topic_mastery:
                profile.topic_mastery[topic_key].score = max(0.1, profile.topic_mastery[topic_key].score - 0.08)
                profile.topic_mastery[topic_key].status = "struggling"
            LearnerProfileManager._sync_weak_topics(profile)
            LearnerProfileManager.estimate_knowledge_level(profile)

    @staticmethod
    def estimate_knowledge_level(profile: LearnerProfile) -> str:
        """
        Smooth, non-hasty Bayesian estimation of overall learner capability.
        Combines onboarded preference, average topic mastery, quiz accuracy, and feedback ratio.
        """
        profile.total_interactions = len(profile.interaction_history) + len(profile.feedback_history)

        if not profile.topic_mastery:
            if profile.onboarded_level and profile.onboarded_level != "let_ai_determine":
                profile.estimated_level = profile.onboarded_level
                profile.level_confidence = 0.5
            else:
                profile.estimated_level = "undetermined"
                profile.level_confidence = 0.2
            return profile.estimated_level

        # Calculate weighted average mastery
        total_weight = sum(m.confidence for m in profile.topic_mastery.values())
        if total_weight == 0:
            return profile.estimated_level

        avg_mastery = sum(m.score * m.confidence for m in profile.topic_mastery.values()) / total_weight

        # Factor in feedback positive ratio
        got_it_count = sum(1 for f in profile.feedback_history if f["feedback_type"] == "got_it")
        confused_count = sum(1 for f in profile.feedback_history if f["feedback_type"] == "still_confused")
        total_feedback = got_it_count + confused_count
        feedback_multiplier = (got_it_count / total_feedback) if total_feedback > 0 else 0.5

        composite_score = (avg_mastery * 0.70) + (feedback_multiplier * 0.30)

        # Thresholds for classification
        if composite_score >= 0.75 and len(profile.topic_mastery) >= 2:
            new_level = "advanced"
        elif composite_score >= 0.45:
            new_level = "intermediate"
        else:
            new_level = "beginner"

        profile.estimated_level = new_level
        profile.level_confidence = min(0.95, 0.4 + (len(profile.topic_mastery) * 0.1) + (profile.total_interactions * 0.05))

        return profile.estimated_level

    @staticmethod
    def _sync_weak_topics(profile: LearnerProfile) -> None:
        """Identify topics where the learner is struggling or scores < 0.50."""
        weak = []
        for key, mastery in profile.topic_mastery.items():
            if mastery.score < 0.55 or mastery.status == "struggling":
                weak.append(mastery.topic)
        profile.weak_topics = list(set(weak))


# Top-level functional helpers for external callers
def get_learner_profile(user_id: str) -> Dict[str, Any]:
    """Retrieve learner profile as a serializable dict."""
    profile = LearnerProfileManager.get_or_create_profile(user_id)
    return profile.to_dict()


def update_learner_profile(user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update profile interaction count and log interaction."""
    profile = LearnerProfileManager.get_or_create_profile(user_id)
    profile.interaction_history.append(interaction_data)
    profile.total_interactions += 1
    return profile.to_dict()


def update_mastery(
    topic: str,
    performance: Union[bool, Dict[str, Any]],
    learner_profile: Optional[Union[LearnerProfile, Dict[str, Any]]] = None
) -> LearnerProfile:
    """
    Standard interface for updating topic mastery.
    """
    if isinstance(learner_profile, LearnerProfile):
        profile = learner_profile
    elif isinstance(learner_profile, dict) and "user_id" in learner_profile:
        profile = LearnerProfileManager.get_or_create_profile(learner_profile["user_id"])
    else:
        profile = LearnerProfileManager.get_or_create_profile("guest_user")

    if isinstance(performance, bool):
        is_correct = performance
        difficulty = "intermediate"
    elif isinstance(performance, dict):
        is_correct = bool(performance.get("is_correct", False))
        difficulty = str(performance.get("difficulty", "intermediate"))
    else:
        is_correct = False
        difficulty = "beginner"

    LearnerProfileManager.update_mastery(profile, topic, is_correct=is_correct, difficulty=difficulty)
    return profile
