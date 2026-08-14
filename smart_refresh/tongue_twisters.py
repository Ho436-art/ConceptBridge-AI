"""
Tongue Twisters Module
Owner: Member 4 (AI/ML + Smart Refresh)

Fun articulation challenges to lighten up the mood during study breaks.
"""

import random
from typing import List

TWISTER_POOL = [
    "She sells seashells by the seashore.",
    "Six sticky skeletons, six slick slime-slipping snakes, silently sliding south.",
    "Peter Piper picked a peck of pickled peppers.",
    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
    "Betty Botter bought some butter, but she said the butter's bitter.",
    "Red leather, yellow leather, red leather, yellow leather.",
    "A proper cup of coffee in a copper coffee pot."
]

def get_tongue_twister() -> str:
    """
    Returns a fun tongue twister to try out loud from a randomized pool.
    """
    return random.choice(TWISTER_POOL)

