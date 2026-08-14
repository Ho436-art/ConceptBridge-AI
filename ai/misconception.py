"""
Misconception Detection Module
Owner: Member 1 (Team Lead / AI & ML)

Responsibilities:
- Lightweight identification of potential cognitive misconceptions from wrong answers,
  student explanations, and repeated mistakes.
- Uses calibrated confidence scores (0.0 to 1.0) and avoids overclaiming diagnostic perfection.
- Provides friendly, constructive remediations to guide learners back on track.
"""

import re
from typing import Dict, Any, Optional, List, Union
from models.schemas import MisconceptionResult, LearnerProfile
from ai.prompts.system_prompts import MISCONCEPTION_ANALYSIS_PROMPT
from ai.llm_client import query_llm_json

# Known diagnostic patterns for common STEM / CS misconceptions
DIAGNOSTIC_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "concept": "recursion",
        "patterns": [
            r"recursion.*always.*loop",
            r"never\s+stops",
            r"doesn'?t\s+need\s+a?\s*base\s*case",
            r"same\s+as\s+while\s+true"
        ],
        "misconception": "Belief that recursion is intrinsically an infinite loop without exit mechanism.",
        "explanation": "Recursion only becomes infinite if the Base Case is missing or unreachable. With a proper base case, each call safely shrinks the problem space.",
        "recommended_correction": "Remember: Always specify the stopping condition (Base Case) first before writing the recursive call.",
        "confidence": 0.85,
        "category": "boundary_case"
    },
    {
        "concept": "binary search",
        "patterns": [
            r"any\s+list",
            r"works\s+on\s+unsorted",
            r"doesn'?t\s+matter\s+if\s+sorted"
        ],
        "misconception": "Assuming Binary Search operates on arbitrary unsorted arrays.",
        "explanation": "Binary search critically depends on sorted order to eliminate half the search space at each comparison. On unsorted data, it will produce false negatives.",
        "recommended_correction": "Before executing Binary Search, ensure the collection is pre-sorted, or use O(N) linear search if sorting is not possible.",
        "confidence": 0.90,
        "category": "prerequisite_gap"
    },
    {
        "concept": "big-o",
        "patterns": [
            r"o\(n\s*log\s*n\)\s+is\s+faster\s+than\s+o\(n\)",
            r"o\(1\)\s+means\s+1\s+second",
            r"faster\s+because\s+fewer\s+lines"
        ],
        "misconception": "Confusing asymptotic growth rate with absolute wall-clock execution time or fewer lines of code.",
        "explanation": "Big-O measures how computation scales as input size N grows towards infinity, not the absolute wall-clock runtime in seconds.",
        "recommended_correction": "Focus on how operations scale with input growth: O(1) < O(log N) < O(N) < O(N log N) < O(N^2).",
        "confidence": 0.88,
        "category": "mental_model"
    },
    {
        "concept": "hash table",
        "patterns": [
            r"never\s+collides",
            r"always\s+guaranteed\s+o\(1\)",
            r"infinite\s+keys\s+without\s+collision"
        ],
        "misconception": "Assuming hash tables are immune to collisions or maintain O(1) in extreme pathological cases.",
        "explanation": "By the Pigeonhole Principle, hash collisions are inevitable when keys exceed bucket capacity. Chaining or probing handles collisions, but bad hashes degrade to O(N).",
        "recommended_correction": "Design high-entropy hash functions and resize tables when load factor exceeds ~0.75.",
        "confidence": 0.82,
        "category": "boundary_case"
    }
]


def detect_misconceptions(
    concept: str,
    student_answer: str,
    expected_concept: Optional[str] = None,
    context: Optional[str] = None,
    learner_profile: Optional[Union[LearnerProfile, Dict[str, Any]]] = None
) -> MisconceptionResult:
    """
    Evaluates student explanation or wrong quiz answer to identify potential cognitive misconceptions.
    
    Args:
        concept: Concept being studied.
        student_answer: The student's text response or selected wrong option.
        expected_concept: Optional expected correct answer / insight.
        context: Optional context of the question.
        learner_profile: Current learner profile state.
        
    Returns:
        MisconceptionResult: Diagnostic outcome with confidence score.
    """
    clean_concept = concept.lower().strip()
    clean_input = student_answer.lower().strip()

    # 1. First, check diagnostic pattern knowledge base for fast, deterministic detection
    for item in DIAGNOSTIC_KNOWLEDGE_BASE:
        if item["concept"] in clean_concept or clean_concept in item["concept"]:
            for pattern in item["patterns"]:
                if re.search(pattern, clean_input):
                    return MisconceptionResult(
                        concept=concept.title(),
                        has_misconception=True,
                        identified_misconception=item["misconception"],
                        explanation=item["explanation"],
                        recommended_correction=item["recommended_correction"],
                        confidence=item["confidence"],
                        underlying_category=item["category"]
                    )

    # 2. Try LLM-based diagnostic analysis if online
    prompt = (
        f"Concept: {concept}\n"
        f"Context / Question: {context or 'General conceptual check'}\n"
        f"Student Answer / Query: {student_answer}\n"
        f"Expected Insight: {expected_concept or 'Accurate conceptual understanding'}"
    )

    llm_diag = query_llm_json(
        prompt=prompt,
        system_prompt=MISCONCEPTION_ANALYSIS_PROMPT,
        fallback_concept=concept
    )

    if llm_diag and isinstance(llm_diag, dict) and "has_misconception" in llm_diag:
        return MisconceptionResult(
            concept=concept.title(),
            has_misconception=bool(llm_diag.get("has_misconception", False)),
            identified_misconception=llm_diag.get("identified_misconception"),
            explanation=llm_diag.get("explanation"),
            recommended_correction=llm_diag.get("recommended_correction"),
            confidence=min(1.0, max(0.0, float(llm_diag.get("confidence", 0.75)))),
            underlying_category=llm_diag.get("underlying_category", "mental_model")
        )

    # 3. Default benign outcome (no high-confidence misconception detected)
    return MisconceptionResult(
        concept=concept.title(),
        has_misconception=False,
        identified_misconception=None,
        explanation=None,
        recommended_correction=None,
        confidence=0.30,
        underlying_category=None
    )
