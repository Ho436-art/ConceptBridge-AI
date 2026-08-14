"""
Technical Memory-Card Game Module
Owner: Member 4 (AI/ML + Smart Refresh)

Lightweight flashcard/matching game pairing terms with definitions, symbols, or code snippets.
"""

import random
from typing import List, Dict

DECKS = {
    "general_cs": [
        {"id": "cs1", "card_a": "Database", "card_b": "SQL"},
        {"id": "cs2", "card_a": "Router", "card_b": "Network"},
        {"id": "cs3", "card_a": "Python", "card_b": "Programming"},
        {"id": "cs4", "card_a": "HTML", "card_b": "Markup"},
        {"id": "cs5", "card_a": "Stack", "card_b": "LIFO (Last In First Out)"},
        {"id": "cs6", "card_a": "Queue", "card_b": "FIFO (First In First Out)"}
    ],
    "data_structures": [
        {"id": "ds1", "card_a": "Array", "card_b": "Contiguous memory slots"},
        {"id": "ds2", "card_a": "Linked List", "card_b": "Nodes connected by pointers"},
        {"id": "ds3", "card_a": "Binary Tree", "card_b": "Each node has at most two children"},
        {"id": "ds4", "card_a": "Graph", "card_b": "Nodes and edges representing networks"},
        {"id": "ds5", "card_a": "Hash Table", "card_b": "Key-value mapping using hashing"},
        {"id": "ds6", "card_a": "Heap", "card_b": "Tree-based structure for priority queues"}
    ],
    "symbols_and_objects": [
        {"id": "so1", "card_a": "☕ Java", "card_b": "Coffee Cup Symbol"},
        {"id": "so2", "card_a": "🐍 Python", "card_b": "Serpent Symbol"},
        {"id": "so3", "card_a": "📦 Docker", "card_b": "Shipping Container Symbol"},
        {"id": "so4", "card_a": "⚙️ Settings", "card_b": "Gear Symbol"},
        {"id": "so5", "card_a": "☁️ Cloud", "card_b": "Remote Servers Symbol"},
        {"id": "so6", "card_a": "🗄️ Database", "card_b": "Filing Cabinet Symbol"}
    ]
}

def get_memory_card_deck(topic: str = "general_cs", limit: int = 4) -> List[Dict[str, str]]:
    """
    Returns a small deck of technical concept cards for matching.
    
    Args:
        topic (str): Category of the deck. Options: general_cs, data_structures, symbols_and_objects.
        limit (int): Maximum number of card pairs to return.
        
    Returns:
        List[Dict[str, str]]: A list of dictionaries representing card pairs.
    """
    selected_deck = DECKS.get(topic, DECKS["general_cs"])
    
    # Pick a random subset of card pairs up to the limit
    sample_size = min(len(selected_deck), limit)
    deck_sample = random.sample(selected_deck, sample_size)
    
    return deck_sample

