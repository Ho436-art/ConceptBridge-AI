"""
Riddles Module
Owner: Member 4 (AI/ML + Smart Refresh)

Lighthearted brain teasers for a mental reset.
"""

import random
from typing import Dict, Any

RIDDLE_POOL = [
    {
        "riddle": "I have keys but no doors. I have space but no room. You can enter but cannot leave. What am I?",
        "hint": "You are probably typing on one right now.",
        "answer": "A Keyboard",
        "explanation": "A computer keyboard has keys (letter keys, command keys), a Spacebar, and an Enter key."
    },
    {
        "riddle": "The more of them you take, the more you leave behind. What are they?",
        "hint": "Think about walking.",
        "answer": "Footsteps",
        "explanation": "When you walk, you take footsteps and leave footsteps/tracks behind you."
    },
    {
        "riddle": "What is full of holes but still holds water?",
        "hint": "You might find it in your kitchen sink.",
        "answer": "A Sponge",
        "explanation": "A sponge has many porous holes to absorb and hold liquid."
    },
    {
        "riddle": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
        "hint": "Listen closely in a canyon.",
        "answer": "An Echo",
        "explanation": "An echo reproduces sound when sound waves bounce off surfaces, needing no vocal cords or ears."
    },
    {
        "riddle": "What gets wetter the more it dries?",
        "hint": "You use it after taking a shower.",
        "answer": "A Towel",
        "explanation": "A towel absorbs moisture from your body to dry it, which makes the towel wetter."
    }
]

def get_riddle() -> Dict[str, Any]:
    """
    Returns a random brain teaser riddle with hidden answer, hint, and explanation.
    """
    return random.choice(RIDDLE_POOL)

