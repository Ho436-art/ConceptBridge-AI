"""
Fun Mathematics Game Module
Owner: Member 4 (AI/ML + Smart Refresh)

Quick mental math puzzles, pattern recognition, and fun numerical riddles.
"""

import random
from typing import Dict, Any

MATH_POOL = [
    {
        "puzzle": "What comes next in the sequence: 2, 4, 8, 16, ___?",
        "options": ["24", "32", "64", "20"],
        "answer": "32",
        "explanation": "Each number is multiplied by 2 to get the next number."
    },
    {
        "puzzle": "If a shirt costs $20 and is on sale for 25% off, what is the sale price?",
        "options": ["$15", "$16", "$12.50", "$18"],
        "answer": "$15",
        "explanation": "25% of 20 is 5, and 20 - 5 = 15."
    },
    {
        "puzzle": "What is the missing number: 1, 3, 6, 10, ___?",
        "options": ["14", "15", "16", "20"],
        "answer": "15",
        "explanation": "The difference increases by 1 each time: +2, +3, +4, so next is +5. 10 + 5 = 15."
    },
    {
        "puzzle": "A train travels at 60 mph. How far does it travel in 2.5 hours?",
        "options": ["120 miles", "150 miles", "160 miles", "180 miles"],
        "answer": "150 miles",
        "explanation": "Distance = Speed * Time = 60 * 2.5 = 150 miles."
    },
    {
        "puzzle": "A clock strikes once at 1 o'clock, twice at 2 o'clock, and so on. How many times does it strike in total in the first 4 hours of a day?",
        "options": ["4 times", "8 times", "10 times", "12 times"],
        "answer": "10 times",
        "explanation": "Sum of strikes: 1 + 2 + 3 + 4 = 10."
    }
]

def get_math_puzzle() -> Dict[str, Any]:
    """
    Returns a quick numerical pattern or puzzle from a randomized pool.
    """
    return random.choice(MATH_POOL)

