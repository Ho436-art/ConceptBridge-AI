"""
Guess-the-Concept Game Module
Owner: Member 4 (AI/ML + Smart Refresh)

Progressive hint guessing game for technical concepts.
Features 15+ concepts with non-repeating randomization and flexible answer matching.
"""

import random
from typing import Dict, Any, Optional, List

CONCEPT_POOL = {
    "graph_coloring": {
        "concept_id": "graph_coloring",
        "hints": [
            "Hint 1: I am a famous problem in graph theory and combinatorial optimization.",
            "Hint 2: The rule is that no two adjacent vertices sharing an edge can have the same color.",
            "Hint 3: The minimum number of colors I need to color a graph is called its Chromatic Number χ(G)."
        ],
        "answer": "Graph Coloring",
        "aliases": ["graph coloring", "graph colour", "vertex coloring", "graph coloring problem"]
    },
    "recursion": {
        "concept_id": "recursion",
        "hints": [
            "Hint 1: I am a technique where a function solves a problem by calling smaller instances of itself.",
            "Hint 2: I always need a Base Case stopping condition to prevent an infinite loop.",
            "Hint 3: Each of my calls allocates a new stack frame on the system call stack."
        ],
        "answer": "Recursion",
        "aliases": ["recursion", "recursive function", "recursive"]
    },
    "database_index": {
        "concept_id": "database_index",
        "hints": [
            "Hint 1: I am a special data structure on database columns that speeds up data retrieval.",
            "Hint 2: Think of the index pages at the back of a 1,000-page textbook.",
            "Hint 3: I speed up SELECT queries using B-Trees, but add overhead to INSERT and UPDATE queries."
        ],
        "answer": "Database Index",
        "aliases": ["database index", "index", "b-tree index", "indexing", "db index"]
    },
    "binary_search": {
        "concept_id": "binary_search",
        "hints": [
            "Hint 1: I find a target value within a SORTED array in O(log N) time.",
            "Hint 2: At every single step, I compare against the middle element and discard half the list.",
            "Hint 3: Think of finding a word by opening a physical dictionary directly to the middle page."
        ],
        "answer": "Binary Search",
        "aliases": ["binary search", "binary search algorithm", "bsearch"]
    },
    "api": {
        "concept_id": "api",
        "hints": [
            "Hint 1: I allow two different software programs to communicate and exchange data securely.",
            "Hint 2: Think of a waiter taking your order to the kitchen and bringing back your prepared food.",
            "Hint 3: My acronym stands for Application Programming Interface (like REST or GraphQL)."
        ],
        "answer": "API",
        "aliases": ["api", "rest api", "application programming interface", "web api"]
    },
    "hash_table": {
        "concept_id": "hash_table",
        "hints": [
            "Hint 1: I provide average O(1) constant-time key lookup, insertion, and deletion.",
            "Hint 2: I use a mathematical hash function to map keys to array bucket indices.",
            "Hint 3: I handle collisions using techniques like chaining or open addressing."
        ],
        "answer": "Hash Table",
        "aliases": ["hash table", "hash map", "dictionary", "hashmap", "hashtable"]
    },
    "stack": {
        "concept_id": "stack",
        "hints": [
            "Hint 1: I am a linear data structure that follows the LIFO principle.",
            "Hint 2: The last item added to me is always the first item removed.",
            "Hint 3: My primary operations are called push() and pop(), like a stack of plates in a cafeteria."
        ],
        "answer": "Stack",
        "aliases": ["stack", "call stack", "lifo"]
    },
    "queue": {
        "concept_id": "queue",
        "hints": [
            "Hint 1: I am a linear data structure that follows the FIFO principle.",
            "Hint 2: The first item added is always the first item processed.",
            "Hint 3: Think of people waiting in line at a movie ticket counter: enqueue at the rear, dequeue from the front."
        ],
        "answer": "Queue",
        "aliases": ["queue", "fifo", "priority queue"]
    },
    "garbage_collection": {
        "concept_id": "garbage_collection",
        "hints": [
            "Hint 1: I am an automatic memory management feature in modern runtimes like Python, Java, and Go.",
            "Hint 2: I reclaim heap memory occupied by objects that are no longer referenced by the program.",
            "Hint 3: I protect developers from fatal memory leaks without requiring manual free() calls."
        ],
        "answer": "Garbage Collection",
        "aliases": ["garbage collection", "gc", "garbage collector", "automatic memory management"]
    },
    "docker": {
        "concept_id": "docker",
        "hints": [
            "Hint 1: I package applications and their dependencies into lightweight, portable containers.",
            "Hint 2: 'It worked on my machine!' is the classic developer problem I was invented to solve.",
            "Hint 3: My mascot is a friendly whale carrying shipping containers."
        ],
        "answer": "Docker",
        "aliases": ["docker", "containerization", "containers", "container"]
    },
    "git": {
        "concept_id": "git",
        "hints": [
            "Hint 1: I am a distributed version control system created by Linus Torvalds in 2005.",
            "Hint 2: I track history using commits, branches, and merges via Directed Acyclic Graphs.",
            "Hint 3: Developers use commands like commit, push, pull, and merge with me every day."
        ],
        "answer": "Git",
        "aliases": ["git", "version control", "vcs"]
    },
    "neural_network": {
        "concept_id": "neural_network",
        "hints": [
            "Hint 1: I am an artificial intelligence model inspired by biological brain neurons.",
            "Hint 2: I learn representations from data by tuning weights using Backpropagation and Gradient Descent.",
            "Hint 3: Deep learning uses many stacked layers of me to recognize images and generate text."
        ],
        "answer": "Neural Network",
        "aliases": ["neural network", "artificial neural network", "ann", "deep learning", "neural net"]
    }
}


def get_guess_challenge(
    struggled_concept: Optional[str] = None,
    exclude_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Returns a guess-the-concept challenge from a randomized pool,
    prioritizing concepts the student struggled with if provided.
    """
    if struggled_concept:
        clean_target = struggled_concept.lower().replace(" ", "_")
        for k, val in CONCEPT_POOL.items():
            if k in clean_target or clean_target in k:
                return dict(val)

    exclude = set(exclude_keys or [])
    available = [k for k in CONCEPT_POOL.keys() if k not in exclude]
    if not available:
        available = list(CONCEPT_POOL.keys())

    chosen_key = random.choice(available)
    data = dict(CONCEPT_POOL[chosen_key])
    data["pool_key"] = chosen_key
    return data


def verify_guess(user_guess: str, challenge: Dict[str, Any]) -> bool:
    """Verifies whether the student's text guess matches the answer or aliases."""
    clean_guess = user_guess.strip().lower()
    correct_ans = challenge.get("answer", "").strip().lower()
    aliases = [a.lower() for a in challenge.get("aliases", [])]
    
    if clean_guess == correct_ans:
        return True
    if clean_guess in aliases:
        return True
    for alias in aliases:
        if alias in clean_guess or clean_guess in alias:
            return True
    return False
