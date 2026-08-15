"""
Tongue Twisters Module
Owner: Member 4 (AI/ML + Smart Refresh)

Fun articulation challenges to lighten up the mood during study breaks.
Features 15+ tongue twisters with non-repeating randomization.
"""

import random
from typing import List, Optional

TWISTER_POOL = [
    "She sells seashells by the seashore.",
    "Six sticky skeletons, six slick slime-slipping snakes, silently sliding south.",
    "Peter Piper picked a peck of pickled peppers.",
    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
    "Betty Botter bought some butter, but she said the butter's bitter.",
    "Red leather, yellow leather, red leather, yellow leather.",
    "A proper cup of coffee in a copper coffee pot.",
    "Fuzzy Wuzzy was a bear. Fuzzy Wuzzy had no hair. Fuzzy Wuzzy wasn't fuzzy, was he?",
    "If a dog chews shoes, whose shoes does he choose?",
    "I scream, you scream, we all scream for ice cream!",
    "Pad kid pour far away potted plant properly.",
    "Which wristwatches are Swiss wristwatches?",
    "Willie's really weary, Willie's really weary.",
    "Selfish shellfish, selfish shellfish, selfish shellfish.",
    "He threw three free throws through the thick hoop."
]


def get_tongue_twister(exclude_indices: Optional[List[int]] = None) -> str:
    """
    Returns a fun tongue twister to try out loud from a randomized pool,
    avoiding recently shown twisters.
    """
    exclude = set(exclude_indices or [])
    available = [idx for idx in range(len(TWISTER_POOL)) if idx not in exclude]
    if not available:
        available = list(range(len(TWISTER_POOL)))

    chosen_idx = random.choice(available)
    return TWISTER_POOL[chosen_idx]
