"""
General Knowledge (GK) Trivia Module
Owner: Member 4 (AI/ML + Smart Refresh)

Light trivia questions for a quick brain refresh.
"""

import random
from typing import List, Dict, Any

TRIVIA_POOL = [
    {
        "question": "Which programming language was originally called 'Oak'?",
        "options": ["Python", "Java", "C++", "Ruby"],
        "answer": "Java"
    },
    {
        "question": "What is the name of the nearest galaxy to our Milky Way?",
        "options": ["Andromeda", "Triangulum", "Sombrero", "Centaurus"],
        "answer": "Andromeda"
    },
    {
        "question": "Which gas do plants absorb from the atmosphere for photosynthesis?",
        "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
        "answer": "Carbon Dioxide"
    },
    {
        "question": "How many bones are there in an adult human body?",
        "options": ["186", "206", "226", "256"],
        "answer": "206"
    },
    {
        "question": "Which element has the chemical symbol 'O'?",
        "options": ["Osmium", "Oxygen", "Gold", "Iron"],
        "answer": "Oxygen"
    },
    {
        "question": "Who is credited with creating the World Wide Web in 1989?",
        "options": ["Bill Gates", "Tim Berners-Lee", "Steve Jobs", "Ada Lovelace"],
        "answer": "Tim Berners-Lee"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic Ocean", "Indian Ocean", "Pacific Ocean", "Arctic Ocean"],
        "answer": "Pacific Ocean"
    },
    {
        "question": "Which animal is known as the 'Ship of the Desert'?",
        "options": ["Horse", "Camel", "Elephant", "Donkey"],
        "answer": "Camel"
    }
]

def get_gk_trivia(limit: int = 1) -> List[Dict[str, Any]]:
    """
    Returns quick GK questions with options from a randomized pool.
    
    Args:
        limit (int): Number of questions to return.
    """
    sample_size = min(len(TRIVIA_POOL), limit)
    return random.sample(TRIVIA_POOL, sample_size)

