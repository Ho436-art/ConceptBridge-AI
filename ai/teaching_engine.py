"""
AI Teaching Engine Module
Owner: Member 1 (Team Lead / AI & ML)

Core Factuality Architecture:
USER QUESTION -> CONCEPT IDENTIFICATION -> VERIFIED KNOWLEDGE BASE -> AI TEACHING ENGINE
-> ANALOGY FIRST -> SIMPLE BREAKDOWN -> TECHNICAL DEEP DIVE -> PRACTICAL EXAMPLE -> DIAGRAM -> CHECK QUESTION

Rules:
- Accuracy is prioritized over creativity.
- Real-world analogies strictly correspond to structural constraints of the concept.
- Real diagrams (Graphviz/Mermaid) attached whenever visual models exist.
- No generic filler educational phrases.
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
from ai.verified_knowledge import lookup_verified_knowledge
from ai.diagram_generator import get_diagram_for_concept


def _normalize_concept_query(concept_query: str) -> str:
    """Extract clean concept name from user prompt."""
    query = concept_query.strip()
    # Remove conversational prefixes
    patterns = [
        r"^explain\s+(to\s+me\s+)?(what\s+is\s+)?(the\s+concept\s+of\s+)?",
        r"^what\s+is\s+(a\s+|an\s+|the\s+)?",
        r"^how\s+does\s+",
        r"^teach\s+me\s+(about\s+)?",
        r"^can\s+you\s+explain\s+",
        r"^tell\s+me\s+about\s+",
        r"^give\s+me\s+an\s+explanation\s+of\s+"
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
    style_override: Optional[str] = None,
    context_document: Optional[str] = None
) -> ConceptExplanation:
    """
    Core AI Teaching Engine entry point with Ground-Truth Factuality Pipeline.
    
    Args:
        concept (str): Concept requested by user (e.g. 'Explain Graph Coloring', 'Recursion').
        learner_profile (LearnerProfile or dict, optional): Current learner profile.
        style_override (str, optional): Target pedagogical style (e.g. 'super_simple', 'step_by_step').
        context_document (str, optional): Attached document text or PDF excerpt.
        
    Returns:
        ConceptExplanation: Strongly typed, structured learning response with real diagram.
    """
    clean_concept = _normalize_concept_query(concept) or concept.strip()
    if clean_concept.lower() in ["this document", "this pdf", "this file", "this code", "this image", "attached file"] and context_document:
        # Extract title from context document
        first_line = context_document.strip().split("\n")[0][:40].strip("- ")
        clean_concept = first_line if first_line else "Uploaded Document Analysis"
    
    # Handle dict input for interoperability
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

    # 1. Pipeline Step: Verified Ground-Truth Knowledge Lookup
    verified_data = lookup_verified_knowledge(clean_concept)
    
    # 2. Pipeline Step: Diagram Resolution
    diag_type, diag_code, diag_caption = get_diagram_for_concept(clean_concept)

    # 3. If verified ground-truth exists, prioritize accuracy
    if verified_data and not context_document:
        json_data = dict(verified_data)
        json_data["difficulty"] = target_level
        json_data["style_used"] = target_style
        
        # If alternative style was requested, customize text style
        if target_style == "super_simple":
            json_data["real_world_analogy"] = f"Imagine in super simple terms: {json_data['simple_explanation']}"
    else:
        # Query LLM with strict factual grounding prompt
        doc_section = f"\n\nATTACHED REFERENCE CONTEXT / DOCUMENT:\n{context_document}\nExplain the concept in accordance with this material." if context_document else ""
        prompt = (
            f"Concept: '{clean_concept}'\n"
            f"Target Learner Knowledge Level: {target_level}\n"
            f"Pedagogical Style: {target_style}{doc_section}\n\n"
            f"STRICT FACTUALITY CONSTRAINTS:\n"
            f"1. Explain '{clean_concept}' with 100% mathematical and technical accuracy.\n"
            f"2. Never invent formulas, non-existent algorithm properties, or pseudo-code.\n"
            f"3. The real-world analogy MUST mathematically/logically map to the exact structural constraints of {clean_concept}.\n"
            f"4. Do NOT output generic educational filler like 'X is a fundamental concept used to solve complex problems efficiently'.\n"
            f"5. Provide an accurate code/example demonstration and an understanding-check question."
        )

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

    # Parse UnderstandingCheck
    check_raw = json_data.get("understanding_check", {})
    if isinstance(check_raw, dict):
        understanding_check = UnderstandingCheck(
            question=check_raw.get("question", f"What is the key rule of {clean_concept}?"),
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

    # Attach diagram if present in verified data or diagram generator
    final_diag_type = json_data.get("diagram_type") or diag_type or "none"
    final_diag_code = json_data.get("diagram_code") or diag_code
    final_diag_caption = json_data.get("diagram_caption") or diag_caption

    explanation = ConceptExplanation(
        concept=json_data.get("concept", clean_concept.title()),
        real_world_analogy=json_data.get("real_world_analogy", "Analogy demonstrating concept."),
        simple_explanation=json_data.get("simple_explanation", "Beginner friendly summary."),
        technical_explanation=json_data.get("technical_explanation", "Technical deep dive."),
        practical_application=json_data.get("practical_application", "Real world production use case."),
        example_code_or_visual=json_data.get("example_code_or_visual", "# Demonstration snippet"),
        understanding_check=understanding_check,
        difficulty=json_data.get("difficulty", target_level),
        confidence=float(json_data.get("confidence", 0.95)),
        style_used=target_style,
        key_takeaways=json_data.get("key_takeaways", [
            f"Understanding {clean_concept} establishes strong technical foundations.",
            "Verify boundary conditions and real-world system constraints."
        ]),
        diagram_type=final_diag_type,
        diagram_code=final_diag_code,
        diagram_caption=final_diag_caption
    )

    return explanation
