"""
Technical Memory-Card Game Module
Owner: Member 4 (AI/ML + Smart Refresh)

Lightweight flashcard/matching game pairing terms with definitions or code snippets.
"""

from typing import List, Dict, Any

def get_memory_card_deck(topic: str = "general_cs") -> List[Dict[str, str]]:
    """
    Returns a small deck of technical concept cards for matching.
    """
    return [
        {"id": "1", "card_a": "Stack", "card_b": "LIFO (Last In First Out)"},
        {"id": "2", "card_a": "Queue", "card_b": "FIFO (First In First Out)"},
        {"id": "3", "card_a": "Hash Map", "card_b": "O(1) average key lookup"}
    ]
