"""
Guess-the-Concept Game Module
Owner: Member 4 (AI/ML + Smart Refresh)

Progressive hint guessing game for technical concepts.
"""

from typing import Dict, Any, List

def get_guess_challenge() -> Dict[str, Any]:
    """
    Returns a concept guessing challenge with progressive hints.
    """
    return {
        "concept_id": "recursion",
        "hints": [
            "Hint 1: I am a function that calls myself.",
            "Hint 2: I always need a base case to prevent an infinite loop.",
            "Hint 3: I make use of the call stack."
        ],
        "answer": "Recursion"
    }
