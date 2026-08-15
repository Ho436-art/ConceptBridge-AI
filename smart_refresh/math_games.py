"""
Fun Mathematics Game Module
Owner: Member 4 (AI/ML + Smart Refresh)

Quick mental math puzzles, pattern recognition, and fun numerical riddles.
Features a rich 20+ question pool with non-repeating randomization.
"""

import random
from typing import Dict, Any, List, Optional

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
        "explanation": "25% of $20 is $5, and $20 - $5 = $15."
    },
    {
        "puzzle": "What is the missing number in the sequence: 1, 3, 6, 10, ___?",
        "options": ["14", "15", "16", "20"],
        "answer": "15",
        "explanation": "The difference increases by 1 each time: +2, +3, +4, so next is +5 (10 + 5 = 15)."
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
    },
    {
        "puzzle": "What is the square root of 144?",
        "options": ["11", "12", "13", "14"],
        "answer": "12",
        "explanation": "12 * 12 = 144."
    },
    {
        "puzzle": "If 3 workers take 6 hours to build a wall, how many hours would 6 workers take at the same rate?",
        "options": ["2 hours", "3 hours", "4 hours", "12 hours"],
        "answer": "3 hours",
        "explanation": "Total worker-hours = 3 * 6 = 18. With 6 workers: 18 / 6 = 3 hours."
    },
    {
        "puzzle": "Which number is the only even prime number?",
        "options": ["0", "2", "4", "6"],
        "answer": "2",
        "explanation": "2 is divisible only by 1 and itself; any larger even number is divisible by 2."
    },
    {
        "puzzle": "What is 15% of 200?",
        "options": ["20", "25", "30", "35"],
        "answer": "30",
        "explanation": "10% of 200 is 20, and 5% is 10. 20 + 10 = 30."
    },
    {
        "puzzle": "Next in pattern: 3, 9, 27, 81, ___?",
        "options": ["162", "243", "324", "108"],
        "answer": "243",
        "explanation": "Each number is multiplied by 3 (81 * 3 = 243)."
    },
    {
        "puzzle": "If you roll a standard 6-sided die, what is the probability of rolling an even number?",
        "options": ["1/6", "1/3", "1/2", "2/3"],
        "answer": "1/2",
        "explanation": "Even numbers are 2, 4, 6 (3 out of 6 outcomes = 1/2 or 50%)."
    },
    {
        "puzzle": "What is the sum of angles inside any triangle?",
        "options": ["90°", "180°", "270°", "360°"],
        "answer": "180°",
        "explanation": "The interior angles of any Euclidean triangle always sum to 180 degrees."
    },
    {
        "puzzle": "If x + 7 = 15, what is the value of 2x - 3?",
        "options": ["10", "13", "16", "19"],
        "answer": "13",
        "explanation": "x = 15 - 7 = 8. Then 2(8) - 3 = 16 - 3 = 13."
    },
    {
        "puzzle": "A runner completes a 400-meter lap in 50 seconds. What is their speed in meters per second?",
        "options": ["6 m/s", "8 m/s", "10 m/s", "12 m/s"],
        "answer": "8 m/s",
        "explanation": "Speed = 400m / 50s = 8 m/s."
    },
    {
        "puzzle": "What is the binary representation of decimal number 10?",
        "options": ["1001", "1010", "1100", "1110"],
        "answer": "1010",
        "explanation": "8 + 2 = 10 -> in binary: 1*8 + 0*4 + 1*2 + 0*1 = 1010."
    },
    {
        "puzzle": "What is 7 factorial (7!) divided by 6 factorial (6!)?",
        "options": ["1", "7", "42", "720"],
        "answer": "7",
        "explanation": "7! / 6! = (7 * 6!) / 6! = 7."
    },
    {
        "puzzle": "If a rectangle has length 8 cm and perimeter 24 cm, what is its width?",
        "options": ["4 cm", "6 cm", "8 cm", "16 cm"],
        "answer": "4 cm",
        "explanation": "Perimeter = 2*(l + w) = 24 -> l + w = 12 -> 8 + w = 12 -> w = 4 cm."
    },
    {
        "puzzle": "What is 2 raised to the power of 8 (2^8)?",
        "options": ["128", "256", "512", "1024"],
        "answer": "256",
        "explanation": "2^8 = 256 (the number of distinct values in an 8-bit byte!)."
    },
    {
        "puzzle": "If you buy 3 apples for $1.50, how much do 10 apples cost?",
        "options": ["$4.50", "$5.00", "$5.50", "$6.00"],
        "answer": "$5.00",
        "explanation": "Each apple is $1.50 / 3 = $0.50. 10 apples * $0.50 = $5.00."
    },
    {
        "puzzle": "Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, ___?",
        "options": ["18", "20", "21", "24"],
        "answer": "21",
        "explanation": "Each term is the sum of the previous two terms: 8 + 13 = 21."
    }
]


def get_math_puzzle(exclude_indices: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Returns a quick numerical pattern or puzzle from a randomized pool,
    avoiding recently shown question indices.
    """
    exclude = set(exclude_indices or [])
    available = [idx for idx in range(len(MATH_POOL)) if idx not in exclude]
    if not available:
        available = list(range(len(MATH_POOL)))

    chosen_idx = random.choice(available)
    data = dict(MATH_POOL[chosen_idx])
    data["puzzle_index"] = chosen_idx
    # Shuffle options randomly
    opts = list(data["options"])
    random.shuffle(opts)
    data["options"] = opts
    return data
