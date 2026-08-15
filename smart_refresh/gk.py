"""
General Knowledge (GK) Trivia Module
Owner: Member 4 (AI/ML + Smart Refresh)

Light trivia questions for a quick brain refresh.
Features a 20+ question pool with non-repeating randomization.
"""

import random
from typing import List, Dict, Any, Optional

TRIVIA_POOL = [
    {
        "question": "Which programming language was originally called 'Oak'?",
        "options": ["Python", "Java", "C++", "Ruby"],
        "answer": "Java"
    },
    {
        "question": "What is the name of the nearest spiral galaxy to our Milky Way?",
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
    },
    {
        "question": "What does 'HTTP' stand for in computer networking?",
        "options": [
            "HyperText Transfer Protocol",
            "High Traffic Transmission Protocol",
            "HyperText Telecom Protocol",
            "Host Terminal Transfer Path"
        ],
        "answer": "HyperText Transfer Protocol"
    },
    {
        "question": "In what year did the Apollo 11 mission first land humans on the Moon?",
        "options": ["1965", "1969", "1972", "1975"],
        "answer": "1969"
    },
    {
        "question": "Who wrote the play 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"],
        "answer": "William Shakespeare"
    },
    {
        "question": "What is the capital city of Japan?",
        "options": ["Kyoto", "Osaka", "Tokyo", "Hiroshima"],
        "answer": "Tokyo"
    },
    {
        "question": "Which planet in our solar system is known as the 'Red Planet'?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "answer": "Mars"
    },
    {
        "question": "What is the hardest natural mineral known on Earth?",
        "options": ["Quartz", "Granite", "Diamond", "Topaz"],
        "answer": "Diamond"
    },
    {
        "question": "How many bits are in a single standard byte?",
        "options": ["4", "8", "16", "32"],
        "answer": "8"
    },
    {
        "question": "What is the chemical formula for water?",
        "options": ["CO2", "H2O", "NaCl", "O2"],
        "answer": "H2O"
    },
    {
        "question": "Which company originally developed the Linux kernel?",
        "options": ["Linus Torvalds (Open Source)", "Microsoft", "Apple", "IBM"],
        "answer": "Linus Torvalds (Open Source)"
    },
    {
        "question": "What is the speed of light in a vacuum (approx)?",
        "options": ["300,000 km/s", "150,000 km/s", "1,000 km/s", "30,000 km/s"],
        "answer": "300,000 km/s"
    },
    {
        "question": "Which is the smallest prime number?",
        "options": ["0", "1", "2", "3"],
        "answer": "2"
    },
    {
        "question": "Which continent is the Sahara Desert located on?",
        "options": ["Asia", "Africa", "South America", "Australia"],
        "answer": "Africa"
    }
]


def get_gk_trivia(limit: int = 1, exclude_indices: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """
    Returns quick GK questions with options from a randomized pool.
    
    Args:
        limit (int): Number of questions to return.
        exclude_indices (list): Indices of questions already seen in this session.
    """
    exclude = set(exclude_indices or [])
    available_indices = [idx for idx in range(len(TRIVIA_POOL)) if idx not in exclude]
    if not available_indices:
        available_indices = list(range(len(TRIVIA_POOL)))

    sample_size = min(len(available_indices), limit)
    chosen_indices = random.sample(available_indices, sample_size)
    
    results = []
    for idx in chosen_indices:
        item = dict(TRIVIA_POOL[idx])
        item["question_index"] = idx
        opts = list(item["options"])
        random.shuffle(opts)
        item["options"] = opts
        results.append(item)

    return results
