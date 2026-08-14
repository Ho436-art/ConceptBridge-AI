"""
General Knowledge (GK) Trivia Module
Owner: Member 4 (AI/ML + Smart Refresh)

Light trivia questions for a quick brain refresh.
"""

from typing import List, Dict, Any

def get_gk_trivia() -> List[Dict[str, Any]]:
    """
    Returns quick GK questions with options.
    """
    return [
        {
            "question": "Which programming language was originally called 'Oak'?",
            "options": ["Python", "Java", "C++", "Ruby"],
            "answer": "Java"
        }
    ]
