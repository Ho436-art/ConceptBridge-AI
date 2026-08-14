"""
Understanding Feedback and Pedagogical Pivot Handler
Owner: Member 1 (Team Lead / AI & ML)

Responsibilities:
- Process understanding feedback ('got_it', 'almost', 'still_confused').
- When 'still_confused' is triggered, pivot the teaching strategy instead of repeating previous text.
- Alternate across: super_simple, step_by_step, visual, practical_code, technical_deep_dive.
- Record style effectiveness to personalize future explanations.
"""

from typing import Dict, Any, Optional, Tuple, Union
from models.schemas import (
    ConceptExplanation,
    LearnerProfile,
    FeedbackType,
    ExplanationStyle
)
from ai.learner_profile import LearnerProfileManager
from ai.teaching_engine import explain_concept

STYLE_PROGRESSION = [
    "analogy_first",
    "super_simple",
    "step_by_step",
    "visual",
    "practical_code",
    "technical_deep_dive"
]


def _select_next_style(current_style: str, profile: Optional[LearnerProfile] = None) -> str:
    """
    Selects the next most effective untried teaching style for a confused learner.
    """
    # If the profile has style effectiveness data, pick the style with highest success rate
    if profile and profile.style_effectiveness:
        ranked_styles = []
        for style, counts in profile.style_effectiveness.items():
            if style == current_style:
                continue
            total = counts.get("got_it", 0) + counts.get("still_confused", 0)
            success_rate = (counts.get("got_it", 0) / total) if total > 0 else 0.5
            ranked_styles.append((success_rate, style))
        if ranked_styles:
            ranked_styles.sort(key=lambda x: x[0], reverse=True)
            return ranked_styles[0][1]

    # Fallback to cyclic progression
    try:
        idx = STYLE_PROGRESSION.index(current_style)
        next_idx = (idx + 1) % len(STYLE_PROGRESSION)
        return STYLE_PROGRESSION[next_idx]
    except ValueError:
        return "super_simple"


def process_feedback(
    feedback: Union[str, FeedbackType],
    concept: str,
    learner_profile: Optional[Union[LearnerProfile, Dict[str, Any]]] = None,
    previous_explanation: Optional[Union[ConceptExplanation, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Core feedback processing interface.
    
    Args:
        feedback (str): 'got_it', 'almost', or 'still_confused'.
        concept (str): Concept being evaluated.
        learner_profile: Target LearnerProfile instance or dict.
        previous_explanation: The explanation that was just shown to the learner.
        
    Returns:
        dict: Payload containing feedback acknowledgement, updated profile summary,
              and (if still_confused) a newly generated alternative explanation.
    """
    clean_feedback = str(feedback).lower().strip()
    
    # Resolve profile
    if isinstance(learner_profile, LearnerProfile):
        profile = learner_profile
    elif isinstance(learner_profile, dict) and "user_id" in learner_profile:
        profile = LearnerProfileManager.get_or_create_profile(learner_profile["user_id"])
    else:
        profile = LearnerProfileManager.get_or_create_profile("guest_user")

    # Extract previous style used
    prev_style = "analogy_first"
    if isinstance(previous_explanation, ConceptExplanation):
        prev_style = previous_explanation.style_used
    elif isinstance(previous_explanation, dict):
        prev_style = previous_explanation.get("style_used", "analogy_first")

    # Record feedback in learner profile
    LearnerProfileManager.record_feedback(
        profile=profile,
        feedback_type=clean_feedback,
        concept=concept,
        style_used=prev_style
    )

    result_payload: Dict[str, Any] = {
        "status": "success",
        "feedback_received": clean_feedback,
        "concept": concept,
        "strategy_changed": False,
        "alternative_explanation": None,
        "encouraging_message": ""
    }

    if clean_feedback in ["got_it", "got it", "crystal_clear"]:
        result_payload["encouraging_message"] = f"🎉 Fantastic job! You've grasped '{concept}'. Ready for the next challenge?"
        
    elif clean_feedback in ["almost", "a bit fuzzy"]:
        result_payload["encouraging_message"] = f"👍 You're almost there with '{concept}'! Review the practical code example above or try the quick check question."
        
    elif clean_feedback in ["still_confused", "still confused", "confused"]:
        # Pivot teaching strategy
        new_style = _select_next_style(prev_style, profile)
        result_payload["strategy_changed"] = True
        result_payload["new_style"] = new_style
        result_payload["encouraging_message"] = (
            f"No worries at all! Let's switch gears and look at '{concept}' using a **{new_style.replace('_', ' ').title()}** approach."
        )
        
        # Generate alternative explanation with fresh angle
        alt_explanation = explain_concept(
            concept=concept,
            learner_profile=profile,
            style_override=new_style
        )
        result_payload["alternative_explanation"] = alt_explanation.to_dict()

    return result_payload
