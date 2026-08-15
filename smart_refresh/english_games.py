"""
English & Vocabulary Activities Module
Owner: Member 4 (AI/ML + Smart Refresh)

Word association, anagrams, and vocabulary puzzles.
Features 15+ word challenges with non-repeating randomization.
"""

import random
from typing import Dict, Any, List, Optional

ENGLISH_POOL = [
    {
        "type": "scramble",
        "scrambled": "HTNPOY",
        "hint": "A popular high-level programming language named after a comedy troupe.",
        "answer": "PYTHON"
    },
    {
        "type": "scramble",
        "scrambled": "MIPLCOER",
        "hint": "Translates high-level source code to executable machine code.",
        "answer": "COMPILER"
    },
    {
        "type": "scramble",
        "scrambled": "AADBTAES",
        "hint": "An organized collection of structured tables, rows, and indexes.",
        "answer": "DATABASE"
    },
    {
        "type": "scramble",
        "scrambled": "MIGTHORLA",
        "hint": "A step-by-step procedure or set of rules to solve a computational problem.",
        "answer": "ALGORITHM"
    },
    {
        "type": "scramble",
        "scrambled": "TRUNERECIS",
        "hint": "When a function calls itself to solve smaller subproblems.",
        "answer": "RECURSION"
    },
    {
        "type": "scramble",
        "scrambled": "WROKTEN",
        "hint": "Interconnected computers and routers sharing packets and data.",
        "answer": "NETWORK"
    },
    {
        "type": "scramble",
        "scrambled": "BLEVARIAB",
        "hint": "A named storage location in computer memory that holds a value.",
        "answer": "VARIABLE"
    },
    {
        "type": "scramble",
        "scrambled": "TIONCFUN",
        "hint": "A reusable block of organized code that takes inputs and returns output.",
        "answer": "FUNCTION"
    },
    {
        "type": "scramble",
        "scrambled": "SEUBGGRD",
        "hint": "A tool or developer who locates and removes software errors.",
        "answer": "DEBUGGER"
    },
    {
        "type": "scramble",
        "scrambled": "ROTCEKOD",
        "hint": "The whale container technology that solved 'it works on my machine'.",
        "answer": "DOCKER"
    },
    {
        "type": "scramble",
        "scrambled": "YECSURTI",
        "hint": "Protecting systems and data from unauthorized digital attacks.",
        "answer": "SECURITY"
    },
    {
        "type": "scramble",
        "scrambled": "MMEORY",
        "hint": "Hardware component (like RAM) used to store immediate runtime data.",
        "answer": "MEMORY"
    },
    {
        "type": "scramble",
        "scrambled": "PAKKET",
        "hint": "A unit of data routed between an origin and destination on the Internet.",
        "answer": "PACKET"
    },
    {
        "type": "scramble",
        "scrambled": "BERWOSR",
        "hint": "Application used to access and view websites on the World Wide Web.",
        "answer": "BROWSER"
    }
]


def get_word_puzzle(exclude_indices: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Returns a random word scramble challenge avoiding recently shown items.
    """
    exclude = set(exclude_indices or [])
    available = [idx for idx in range(len(ENGLISH_POOL)) if idx not in exclude]
    if not available:
        available = list(range(len(ENGLISH_POOL)))

    chosen_idx = random.choice(available)
    data = dict(ENGLISH_POOL[chosen_idx])
    data["puzzle_index"] = chosen_idx
    return data
