"""
Technical Memory-Card Game Module
Owner: Member 4 (AI/ML + Smart Refresh)

Lightweight flashcard/matching game pairing terms with definitions, symbols, or code snippets.
Features rich deck categories and non-repeating shuffle.
"""

import random
from typing import List, Dict, Optional

DECKS = {
    "general_cs": [
        {"id": "cs1", "card_a": "Database", "card_b": "Organized SQL / Table Storage"},
        {"id": "cs2", "card_a": "Router", "card_b": "Directs Network Data Packets"},
        {"id": "cs3", "card_a": "Python", "card_b": "Dynamic Interpreted Language"},
        {"id": "cs4", "card_a": "HTML", "card_b": "Web Document Markup Standard"},
        {"id": "cs5", "card_a": "Stack", "card_b": "LIFO (Last In First Out)"},
        {"id": "cs6", "card_a": "Queue", "card_b": "FIFO (First In First Out)"},
        {"id": "cs7", "card_a": "Git", "card_b": "Distributed Version Control"},
        {"id": "cs8", "card_a": "REST API", "card_b": "HTTP JSON Web Endpoints"},
        {"id": "cs9", "card_a": "Compiler", "card_b": "Translates Source to Machine Code"},
        {"id": "cs10", "card_a": "RAM", "card_b": "Volatile Fast Working Memory"}
    ],
    "data_structures": [
        {"id": "ds1", "card_a": "Array", "card_b": "Contiguous memory slots"},
        {"id": "ds2", "card_a": "Linked List", "card_b": "Nodes connected by pointers"},
        {"id": "ds3", "card_a": "Binary Tree", "card_b": "Each node has at most 2 children"},
        {"id": "ds4", "card_a": "Graph", "card_b": "Nodes connected by weighted/unweighted edges"},
        {"id": "ds5", "card_a": "Hash Table", "card_b": "O(1) key-value hash mapping"},
        {"id": "ds6", "card_a": "Heap", "card_b": "Tree structure for Priority Queues"},
        {"id": "ds7", "card_a": "B-Tree", "card_b": "Balanced disk index tree structure"},
        {"id": "ds8", "card_a": "Trie", "card_b": "Prefix tree for fast string autocomplete"}
    ]
}


def get_memory_card_deck(topic: str = "general_cs", limit: int = 3) -> List[Dict[str, str]]:
    """
    Returns a small deck of technical concept cards for matching.
    
    Args:
        topic (str): Category of the deck. Options: general_cs, data_structures.
        limit (int): Number of card pairs (e.g. 3 pairs = 6 cards).
        
    Returns:
        List[Dict[str, str]]: A list of card pairs.
    """
    selected_deck = DECKS.get(topic, DECKS["general_cs"])
    sample_size = min(len(selected_deck), limit)
    deck_sample = random.sample(selected_deck, sample_size)
    return deck_sample
