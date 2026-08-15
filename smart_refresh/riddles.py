"""
Riddles Module
Owner: Member 4 (AI/ML + Smart Refresh)

Lighthearted brain teasers for a mental reset.
Features 15+ riddles with non-repeating randomization.
"""

import random
from typing import Dict, Any, List, Optional

RIDDLE_POOL = [
    {
        "riddle": "I have keys but no locks. I have space but no room. You can enter but cannot go outside. What am I?",
        "hint": "You are probably typing on one right now.",
        "answer": "A Keyboard",
        "explanation": "A computer keyboard has letter keys, a Spacebar, and an Enter key."
    },
    {
        "riddle": "The more of them you take, the more you leave behind. What are they?",
        "hint": "Think about taking a walk on a sandy beach.",
        "answer": "Footsteps",
        "explanation": "When you walk forward, you take steps and leave your footprints behind."
    },
    {
        "riddle": "What is full of holes but still holds water?",
        "hint": "You use it in the kitchen or bath.",
        "answer": "A Sponge",
        "explanation": "A sponge has many porous holes that absorb and retain liquid."
    },
    {
        "riddle": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind and sound. What am I?",
        "hint": "Listen closely when shouting in a mountain canyon.",
        "answer": "An Echo",
        "explanation": "An echo bounces sound waves back without having physical anatomy."
    },
    {
        "riddle": "What gets wetter the more it dries?",
        "hint": "You use it every day after taking a shower.",
        "answer": "A Towel",
        "explanation": "A towel absorbs moisture from your body to dry you, making itself wetter in the process."
    },
    {
        "riddle": "What has a head and a tail, but no body?",
        "hint": "You flip it to make decisions.",
        "answer": "A Coin",
        "explanation": "A standard coin has heads and tails sides, but no biological body."
    },
    {
        "riddle": "What can travel around the world while staying stuck in one corner?",
        "hint": "You stick it on an envelope before mailing.",
        "answer": "A Postage Stamp",
        "explanation": "A stamp stays glued in the corner of an envelope as the letter travels globally."
    },
    {
        "riddle": "Forward I am heavy, but backward I am not. What am I?",
        "hint": "Look at the spelling of the word 'ton'.",
        "answer": "The word 'TON' (backward it spells 'NOT')",
        "explanation": "A ton weighs 2,000 pounds (heavy), but spelt backward it is the word 'not'."
    },
    {
        "riddle": "What has many teeth, but cannot bite?",
        "hint": "You use it in the morning on your hair.",
        "answer": "A Comb",
        "explanation": "A comb has fine teeth for styling hair, but cannot bite anything."
    },
    {
        "riddle": "What invention lets you look right through a solid wall?",
        "hint": "Almost every room has at least one.",
        "answer": "A Window",
        "explanation": "A glass window lets you see directly through an exterior or interior wall."
    },
    {
        "riddle": "I have branches, but no fruit, trunk, or leaves. What am I?",
        "hint": "Think about finances or Git repositories.",
        "answer": "A Bank (or a Git repository!)",
        "explanation": "Both commercial banks and Git repositories have branches without being biological trees."
    },
    {
        "riddle": "What can you catch, but never throw?",
        "hint": "Achuu! Wear a warm jacket in the winter.",
        "answer": "A Cold",
        "explanation": "You can catch a cold illness, but you cannot throw it physically."
    },
    {
        "riddle": "What building has the most stories in the entire world?",
        "hint": "Where do you go to read books?",
        "answer": "The Library",
        "explanation": "A library contains thousands of fictional and non-fictional stories."
    },
    {
        "riddle": "What goes up, but never comes down?",
        "hint": "It increases with every birthday.",
        "answer": "Your Age",
        "explanation": "Your chronological age only increases over time."
    },
    {
        "riddle": "The person who makes it has no need of it; the person who buys it has no use for it; the person who uses it can neither see nor feel it. What is it?",
        "hint": "Think about eternal resting places.",
        "answer": "A Coffin",
        "explanation": "A classic philosophical riddle where the occupant has passed away."
    }
]


def get_riddle(exclude_indices: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Returns a random brain teaser riddle with hidden answer, hint, and explanation,
    avoiding repeating recently shown riddles.
    """
    exclude = set(exclude_indices or [])
    available = [idx for idx in range(len(RIDDLE_POOL)) if idx not in exclude]
    if not available:
        available = list(range(len(RIDDLE_POOL)))

    chosen_idx = random.choice(available)
    data = dict(RIDDLE_POOL[chosen_idx])
    data["riddle_index"] = chosen_idx
    return data
