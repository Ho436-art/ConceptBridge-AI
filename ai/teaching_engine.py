"""
AI Teaching Engine Module
Owner: Member 1 (Team Lead / AI & ML)

Responsibilities:
- Explain academic and technical concepts using real-world analogies first.
- Provide simple, beginner-friendly explanations alongside technical deep dives.
- Provide practical real-world applications and code/visual demonstrations.
- Adapt explanations dynamically to the learner's estimated knowledge profile.
- Provide interactive understanding-check questions.
- Does NOT assume learner level from a single prompt; calibrates incrementally.
"""

import re
from typing import Dict, Any, Optional, Union
from models.schemas import (
    ConceptExplanation,
    UnderstandingCheck,
    LearnerProfile,
    LearnerLevel,
    ExplanationStyle
)
from ai.prompts.system_prompts import (
    CONCEPTBRIDGE_TEACHER_SYSTEM_PROMPT,
    ALTERNATIVE_STYLE_PROMPT
)
from ai.llm_client import query_llm_json, generate_structured_explanation_fallback


def _normalize_concept_query(concept_query: str) -> str:
    """Extract clean concept name from user prompt."""
    query = concept_query.strip()
    # Remove conversational prefixes
    patterns = [
        r"^explain\s+(to\s+me\s+)?(what\s+is\s+)?(the\s+concept\s+of\s+)?",
        r"^what\s+is\s+(a\s+|an\s+|the\s+)?",
        r"^how\s+does\s+",
        r"^teach\s+me\s+(about\s+)?",
        r"^can\s+you\s+explain\s+"
    ]
    for pattern in patterns:
        query = re.sub(pattern, "", query, flags=re.IGNORECASE).strip()
    return query.rstrip("?.!").strip()


def _resolve_learner_difficulty(learner_profile: Optional[LearnerProfile] = None) -> str:
    """
    Carefully resolves targeted difficulty level without making hasty one-prompt stereotypes.
    """
    if not learner_profile:
        return "beginner"
    
    # 1. Check dynamic estimated level if sufficient interactions occurred
    if learner_profile.estimated_level and learner_profile.estimated_level != "undetermined":
        return learner_profile.estimated_level
    
    # 2. Check onboarded preference if specified
    if learner_profile.onboarded_level and learner_profile.onboarded_level not in ["let_ai_determine", "undetermined"]:
        return learner_profile.onboarded_level
        
    return "beginner"


def explain_concept(
    concept: str,
    learner_profile: Optional[Union[LearnerProfile, Dict[str, Any]]] = None,
    style_override: Optional[str] = None
) -> ConceptExplanation:
    """
    Core AI Teaching Engine entry point.
    
    Args:
        concept (str): Concept requested by user (e.g. 'Explain recursion', 'Binary Search').
        learner_profile (LearnerProfile or dict, optional): Current learner profile.
        style_override (str, optional): Target pedagogical style (e.g. 'super_simple', 'step_by_step').
        
    Returns:
        ConceptExplanation: Strongly typed, structured learning response.
    """
    clean_concept = _normalize_concept_query(concept) or concept.strip()
    
    # Handle dict input for interoperability with other modules
    profile_obj: Optional[LearnerProfile] = None
    if isinstance(learner_profile, dict):
        profile_obj = LearnerProfile(
            user_id=learner_profile.get("user_id", "guest"),
            estimated_level=learner_profile.get("estimated_level", "undetermined"),
            onboarded_level=learner_profile.get("onboarded_level", "let_ai_determine"),
            preferred_style=learner_profile.get("preferred_style", "analogy_first")
        )
    elif isinstance(learner_profile, LearnerProfile):
        profile_obj = learner_profile

    target_level = _resolve_learner_difficulty(profile_obj)
    target_style = style_override or (profile_obj.preferred_style if profile_obj else "analogy_first")

    # Build prompt
    prompt = (
        f"Explain the concept: '{clean_concept}'\n"
        f"Target Learner Knowledge Level: {target_level}\n"
        f"Pedagogical Style: {target_style}\n"
        f"Ensure real-world analogy is vivid, technical explanation is accurate, and understanding check is precise."
    )

    # Query LLM or intelligent fallback
    json_data = query_llm_json(
        prompt=prompt,
        system_prompt=CONCEPTBRIDGE_TEACHER_SYSTEM_PROMPT,
        fallback_concept=clean_concept
    )

    if not json_data or not isinstance(json_data, dict):
        json_data = generate_structured_explanation_fallback(
            concept=clean_concept,
            level=target_level,
            style=target_style
        )

    # Parse and validate UnderstandingCheck
    check_raw = json_data.get("understanding_check", {})
    if isinstance(check_raw, dict):
        understanding_check = UnderstandingCheck(
            question=check_raw.get("question", f"What is the key takeaway of {clean_concept}?"),
            options=check_raw.get("options", [
                "A) Correct fundamental mechanism",
                "B) Common misconception",
                "C) Unrelated concept"
            ]),
            correct_answer=check_raw.get("correct_answer", "A) Correct fundamental mechanism"),
            explanation=check_raw.get("explanation", "Matches core conceptual mechanics."),
            concept_tested=check_raw.get("concept_tested", clean_concept)
        )
    else:
        understanding_check = UnderstandingCheck(
            question=f"What is the core principle behind {clean_concept}?",
            options=["A) Proper conceptual mechanism", "B) False assumption", "C) Syntax error"],
            correct_answer="A) Proper conceptual mechanism",
            explanation="Reflects the fundamental architecture of the concept.",
            concept_tested=clean_concept
        )

    explanation = ConceptExplanation(
        concept=json_data.get("concept", clean_concept.title()),
        real_world_analogy=json_data.get("real_world_analogy", "Analogy demonstrating concept."),
        simple_explanation=json_data.get("simple_explanation", "Beginner friendly summary."),
        technical_explanation=json_data.get("technical_explanation", "Technical deep dive."),
        practical_application=json_data.get("practical_application", "Real world production use case."),
        example_code_or_visual=json_data.get("example_code_or_visual", "# Demonstration snippet"),
        understanding_check=understanding_check,
        difficulty=json_data.get("difficulty", target_level),
        confidence=float(json_data.get("confidence", 0.90)),
        style_used=target_style,
        key_takeaways=json_data.get("key_takeaways", [
            f"Understanding {clean_concept} builds solid engineering foundations.",
            "Always inspect practical trade-offs and edge cases."
        ])
    )

    return explanation


def answer_follow_up(concept: str, question: str, learner_profile: Optional[Dict[str, Any]] = None) -> str:
    """
    Answers a follow-up question on a concept based on the learner's estimated knowledge level.
    """
    level = "beginner"
    if learner_profile:
        if isinstance(learner_profile, dict):
            level = learner_profile.get("estimated_level", "beginner")
        else:
            level = getattr(learner_profile, "estimated_level", "beginner")
            
    # Generic structured responses for high aesthetic display quality
    concept_lower = concept.lower()
    
    if "recursion" in concept_lower:
        if "base case" in question.lower():
            return "Excellent question! A **base case** is the most crucial part of a recursive function. \n\n" \
                   "**Why we need it:** Without a base case, the function keeps calling itself forever, filling up the call stack until you get a `RecursionError: maximum recursion depth exceeded` (known as a stack overflow). \n\n" \
                   "**Example:** In our doll analogy, the base case is the smallest, solid doll that doesn't open. In code, it is usually a simple `if` condition: `if n <= 1: return 1`."
        elif "stack overflow" in question.lower() or "limit" in question.lower():
            return "A **stack overflow** occurs because each recursive call requires memory to store its arguments and variables. This memory is stored in stack frames. \n\n" \
                   "Python has a default recursion limit of **1000 calls**. If your recursion goes deeper than that, Python stops it automatically. You can increase this using `sys.setrecursionlimit()`, but it is usually better to optimize your algorithm (or use loops) to prevent stack build-up."
                   
    # Generic fallback
    return f"Regarding your question *'{question}'* about **{concept}**:\n\n" \
           f"Here is an explanation tailored to your **{level}** level:\n\n" \
           f"1. **Core Concept Connection:** This relates directly to how state and variables are managed in the background.\n" \
           f"2. **Real-world Insight:** Think of it like reading the index of a book. Instead of reading the whole book again, you are zooming in on this specific page.\n" \
           f"3. **Practical Tip:** When implementing this, start by testing the simplest possible input (e.g. `None`, `0` or empty lists) to check how your logic behaves under basic inputs.\n\n" \
           f"Let me know if you would like me to show a code snippet or another analogy!"
