"""
English & Vocabulary Activities Module
Owner: Member 4 (AI/ML + Smart Refresh)

Word association, anagrams, and vocabulary puzzles.
"""

import random
from typing import Dict, Any

ENGLISH_POOL = [
    {
        "type": "scramble",
        "scrambled": "HTNPOY",
        "hint": "A popular dynamic language named after a comedy troupe.",
        "answer": "PYTHON"
    },
    {
        "type": "scramble",
        "scrambled": "MIPLCOER",
        "hint": "Translates high-level source code to machine code.",
        "answer": "COMPILER"
    },
    {
        "type": "scramble",
        "scrambled": "AADBTAES",
        "hint": "An organized collection of structured information or data.",
        "answer": "DATABASE"
    },
    {
        "type": "association",
        "word": "Algorithm",
        "hint": "Which word is most closely associated with 'Algorithm'?",
        "options": ["Recipe", "Painting", "Song", "Sculpture"],
        "answer": "Recipe"
    },
    {
        "type": "vocabulary",
        "word": "Redundant",
        "hint": "What does the word 'Redundant' mean?",
        "options": ["Necessary", "No longer needed or useful", "Extremely fast", "Difficult to read"],
        "answer": "No longer needed or useful"
    }
]

def get_word_puzzle() -> Dict[str, Any]:
    """
    Returns a random word scramble, association, or vocabulary challenge.
    """
    return random.choice(ENGLISH_POOL)

