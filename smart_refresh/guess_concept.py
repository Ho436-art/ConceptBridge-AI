"""
Guess-the-Concept Game Module
Owner: Member 4 (AI/ML + Smart Refresh)

Progressive hint guessing game for technical concepts.
"""

import random
from typing import Dict, Any, Optional

CONCEPT_POOL = {
    "recursion": {
        "concept_id": "recursion",
        "hints": [
            "Hint 1: I am a function that calls itself.",
            "Hint 2: I always need a base case to prevent an infinite loop.",
            "Hint 3: I make use of the call stack."
        ],
        "answer": "Recursion"
    },
    "database_index": {
        "concept_id": "database_index",
        "hints": [
            "Hint 1: I help you find database information faster.",
            "Hint 2: Think about how you look up topics in a physical book.",
            "Hint 3: I speed up SELECT queries but can slow down INSERTs."
        ],
        "answer": "Database Index"
    },
    "binary_search": {
        "concept_id": "binary_search",
        "hints": [
            "Hint 1: I find a target value within a sorted list.",
            "Hint 2: In every step, I divide the search interval in half.",
            "Hint 3: My time complexity is O(log n)."
        ],
        "answer": "Binary Search"
    },
    "api": {
        "concept_id": "api",
        "hints": [
            "Hint 1: I allow two different software programs to communicate with each other.",
            "Hint 2: Think of a waiter taking your order to the kitchen and bringing food back.",
            "Hint 3: My name stands for Application Programming Interface."
        ],
        "answer": "API"
    },
    "garbage_collection": {
        "concept_id": "garbage_collection",
        "hints": [
            "Hint 1: I am an automatic memory management process.",
            "Hint 2: I reclaim memory occupied by objects that are no longer in use.",
            "Hint 3: I prevent memory leaks by sweeping unused memory."
        ],
        "answer": "Garbage Collection"
    }
}

def get_guess_challenge(struggled_concept: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a concept guessing challenge with progressive hints.
    
    If struggled_concept is provided, it tries to match a relevant concept from the pool.
    Otherwise, it picks a random concept from the pool.
    """
    if struggled_concept:
        # Simple lookup: check if any key in CONCEPT_POOL is in the struggled concept name
        normalized_str = struggled_concept.lower().replace(" ", "_")
        for key, challenge in CONCEPT_POOL.items():
            if key in normalized_str or normalized_str in key:
                return challenge
                
    # Fallback to random concept from the pool
    random_key = random.choice(list(CONCEPT_POOL.keys()))
    return CONCEPT_POOL[random_key]

