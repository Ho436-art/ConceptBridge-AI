"""
Teaching Engine Module
Owner: Member 1 (Team Lead / AI & ML)

Responsibilities:
- Explain concepts using real-world analogies first
- Generate simple, beginner-friendly explanations
- Provide technical deep-dive explanations
- Provide practical/code examples and visual explanations
- Adapt explanation style to estimated knowledge level
"""

from typing import Dict, Any, Optional

RICH_EXPLANATIONS = {
    "recursion": {
        "concept": "Recursion",
        "analogy": "Think of **Recursion** like a set of **Russian Nesting Dolls** (Matryoshka dolls). You open the outer doll, only to find a slightly smaller doll inside. You keep opening them (representing the *recursive call*) until you reach the smallest, solid doll that cannot be opened any further (the *base case*). Once you inspect it, you close them back up, doll by doll, returning back to where you started (returning up the *call stack*).",
        "beginner_explanation": "In programming, recursion is simply when **a function calls itself** to solve a problem. It breaks a big task down into smaller, identical tasks. To prevent the function from calling itself forever and crashing your computer, you must write a **base case**—a simple rule that tells the function: *'Stop calling yourself here, we are done!'*",
        "technical_explanation": "Mathematically and computationally, a recursive function solves a problem by applying the same logic to smaller subproblems. Each recursive call pushes a new **activation record (stack frame)** onto the system **call stack**, preserving the function's local variables, arguments, and return address. If recursion is too deep without resolving, it consumes all stack space, leading to a **Stack Overflow**. Many languages optimize tail recursion, where the recursive call is the final operation in the function, avoiding stack frame buildup.",
        "practical_example": """```python
def factorial(n):
    # 1. Base Case: stop calling ourselves when n is 0 or 1
    if n <= 1:
        return 1
    
    # 2. Recursive Case: solve a smaller version of the problem
    return n * factorial(n - 1)

# Let's run it!
print("Factorial of 5 is:", factorial(5))  # Output: 120
```""",
        "visual_explanation": """factorial(3)
 └── 3 * factorial(2)
        └── 2 * factorial(1)
               └── 1 (Base Case reached! Returns 1)
        Returns: 2 * 1 = 2
 Returns: 3 * 2 = 6"""
    },
    "neural_networks": {
        "concept": "Neural Networks",
        "analogy": "Think of a **Neural Network** like a **large company making a decision**. The entry-level employees receive raw data (inputs), summarize it, and pass it to middle managers. The managers weigh the summaries, combine them, and pass their report to the executives (hidden layers). The executives make the final decision (outputs). If the decision is wrong, the boss points out the error, and this feedback flows back down the ladder, causing everyone to adjust how they filter information next time (*backpropagation*).",
        "beginner_explanation": "A neural network is a computer system designed to mimic how the human brain learns. It consists of layers of 'nodes' (like virtual brain cells). By feeding it thousands of examples, it learns to recognize patterns (like identifying a cat in a photo) by adjusting how much weight it gives to different features in the image (like lines, shapes, or whiskers).",
        "technical_explanation": "An Artificial Neural Network (ANN) consists of input, hidden, and output layers of interconnected neurons. Each connection has an associated weight and bias. A neuron computes the weighted sum of its inputs, adds a bias, and passes it through an **activation function** (e.g., ReLU, Sigmoid) to introduce non-linearity. Training involves a **loss function** to measure error and an optimizer (e.g., SGD, Adam) that uses **gradient descent** and **backpropagation** to calculate the partial derivatives of the loss with respect to weights, adjusting them to minimize error.",
        "practical_example": """```python
# Simple representation of a neuron cell in Python
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def neuron(inputs, weights, bias):
    # Weighted sum: w1*x1 + w2*x2 + ... + bias
    weighted_sum = sum(i * w for i, w in zip(inputs, weights)) + bias
    # Pass through activation function
    return sigmoid(weighted_sum)

# Inputs: [height, weight], Weights: [0.8, -0.4], Bias: -0.1
output = neuron([1.7, 70], [0.8, -0.4], -0.1)
print("Activation level:", output)
```""",
        "visual_explanation": """[Input X1] ──(w1)──> 👤 [Neuron] ──> [Output Y]
[Input X2] ──(w2)──/     ↑ (adds Bias)
                         
Calculates: Act(X1*w1 + X2*w2 + Bias)"""
    },
    "pca": {
        "concept": "Principal Component Analysis (PCA)",
        "analogy": "Imagine taking a **3D shadow puppet picture of a complex teapot**. If you take the photo from above, it just looks like a circle. If you take it from the side, you see the handle and the spout in full detail. PCA is like finding that **perfect side-view angle** that captures the most shape, allowing you to represent a 3D object in 2D without losing the key features.",
        "beginner_explanation": "PCA is a technique used to simplify complex datasets with many columns (dimensions) into fewer columns (principal components) while keeping most of the important information. It helps visualize massive data files and speeds up machine learning models.",
        "technical_explanation": "PCA is an unsupervised dimensionality reduction method. It computes the **covariance matrix** of the data, performs **eigendecomposition** to obtain **eigenvalues** and **eigenvectors**, and projects the data onto the eigenvectors associated with the largest eigenvalues (the Principal Components). This maximizes the variance of the projected data while ensuring orthogonal (uncorrelated) components. Data standardisation (mean centering and scaling) is a crucial preprocessing step.",
        "practical_example": """```python
import numpy as np
from sklearn.decomposition import PCA

# Sample 2D data: 3 samples, 2 features
X = np.array([[1, 2], [3, 4], [5, 6]])

# Reduce to 1 dimension
pca = PCA(n_components=1)
X_reduced = pca.fit_transform(X)

print("Original shape:", X.shape)
print("Reduced shape:", X_reduced.shape)
print("Explained Variance Ratio:", pca.explained_variance_ratio_)
```""",
        "visual_explanation": """    Feature Y
       │      / (Principal Component 1 - Direction of Max Variance)
       │    *
       │   *  *
       │ *  *
       └─────────── Feature X
PCA rotates the axes to line up with the variance!"""
    },
    "database_indexing": {
        "concept": "Database Indexing",
        "analogy": "Imagine looking for the word **'Recursion'** in a **500-page programming textbook**. Without an index, you would have to flip through the book page-by-page from the start (a *full table scan*). If you flip to the **Index at the back**, you quickly look up 'R', find 'Recursion: page 142', and jump straight there. The book index is a database index!",
        "beginner_explanation": "Database indexing is a way to speed up search queries on a database table. By creating a separate, organized reference list (the index), the database can find rows instantly instead of scanning the whole database table row by row.",
        "technical_explanation": "A database index is a auxiliary data structure (typically a **B-Tree**, **B+ Tree**, or **Hash index**) that stores pointers to rows in a table. B+ Trees maintain sorted keys with leaf nodes linked together, allowing both point queries and range scans in logarithmic time $O(\\log n)$. Creating an index improves read query performance but introduces write overhead since the index structure must be updated during INSERT, UPDATE, or DELETE operations.",
        "practical_example": """```sql
-- Query without index (scans every row)
SELECT * FROM users WHERE email = 'test@example.com';

-- Creating an index on the email column
CREATE INDEX idx_users_email ON users(email);

-- Query with index (instant lookup via B-Tree)
SELECT * FROM users WHERE email = 'test@example.com';
```""",
        "visual_explanation": """           [ Root Node: Key 50 ]
              /             \\
      [ Leaf: Keys < 50 ]   [ Leaf: Keys >= 50 ]
      [ 10 -> Row Pointer]  [ 50 -> Row Pointer ]
      [ 20 -> Row Pointer]  [ 70 -> Row Pointer ]"""
    },
    "git_version_control": {
        "concept": "Git Version Control",
        "analogy": "Think of **Git** like playing a **video game with unlimited save points**. Before you enter a dangerous boss fight (or write risky code), you save your game state (*git commit*). If you make a mistake and lose all your health, you don't start the whole game over; you simply load your last save state (*git checkout*). You can also branch off to try optional side-quests (*git branch*) and merge them back later (*git merge*).",
        "beginner_explanation": "Git is a tool that tracks changes to files over time. It allows you to save snapshots of your progress, review past edits, work on experimental code safely, and collaborate with other developers without overwriting each other's work.",
        "technical_explanation": "Git is a distributed version control system. It represents history as a Directed Acyclic Graph (DAG) of commit objects. Each commit points to a snapshot of the project directory (stored as a **tree** of **blob** objects) and references parent commits. Branches are simply lightweight, mutable pointers to specific commits. Git uses content-addressable storage (SHA-1/SHA-256 hashes) to ensure history integrity.",
        "practical_example": """```bash
# Initialize a new git repository
git init

# Stage changes for commit
git add main.py

# Record the snapshot with a message
git commit -m "Initialize project structure"

# Create and switch to a feature branch
git checkout -b feature/ui
```""",
        "visual_explanation": """[Commit A] ──> [Commit B] ──> [Commit C]  (develop)
                  \\
                   └──> [Commit D] ──> [Commit E]  (feature/ui)"""
    }
}

def explain_concept(concept: str, learner_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Core interface for generating a multi-tier concept explanation.
    """
    # Lookup in our rich predefined database
    concept_key = concept.strip().lower().replace(" ", "_")
    if concept_key in RICH_EXPLANATIONS:
        data = RICH_EXPLANATIONS[concept_key].copy()
        data["knowledge_level_targeted"] = learner_profile.get("estimated_level", "beginner") if learner_profile else "beginner"
        return data
        
    # Standard fuzzy matching
    for key, value in RICH_EXPLANATIONS.items():
        if key in concept_key or concept_key in key:
            data = value.copy()
            data["knowledge_level_targeted"] = learner_profile.get("estimated_level", "beginner") if learner_profile else "beginner"
            return data
            
    # Fallback to dynamic placeholder
    return {
        "concept": concept,
        "analogy": f"Think of **{concept}** like a **baking recipe**. You follow the steps one by one to get a cake. If you miss a step or change ingredients, the result changes. In the real world, this describes a structured workflow.",
        "beginner_explanation": f"Simply put, **{concept}** is a process or system designed to achieve a specific outcome. It helps break down complex tasks into standard, readable instructions that are easy to follow.",
        "technical_explanation": f"In technical terms, **{concept}** operates as an algorithmic model or procedural layout. It manages state transitions, ensures process synchronization, and maintains deterministic outcomes under defined boundary conditions.",
        "practical_example": f"```python\\n# Simple demonstration of {concept}\\ndef demonstrate_{concept_key}():\\n    # Initialize state\\n    state = 'active'\\n    print('Running demonstration of {concept} in state:', state)\\n\\ndemonstrate_{concept_key}()\\n```",
        "visual_explanation": f"[Input State] ──> [Process {concept}] ──> [Output State]",
        "knowledge_level_targeted": learner_profile.get("estimated_level", "beginner") if learner_profile else "beginner"
    }

def answer_follow_up(concept: str, question: str, learner_profile: Optional[Dict[str, Any]] = None) -> str:
    """
    Answers a follow-up question on a concept based on the learner's estimated knowledge level.
    """
    level = learner_profile.get("estimated_level", "beginner") if learner_profile else "beginner"
    
    # Check if we have specific follow-up questions
    concept_lower = concept.lower()
    
    if "recursion" in concept_lower:
        if "base case" in question.lower():
            return "Excellent question! A **base case** is the most crucial part of a recursive function. \n\n" \
                   "**Why we need it:** Without a base case, the function keeps calling itself forever, filling up the call stack until you get a `RecursionError: maximum recursion depth exceeded` (known as a stack overflow). \n\n" \
                   "**Example:** In our doll analogy, the base case is the smallest, solid doll that doesn't open. In code, it is usually a simple `if` condition: `if n <= 1: return 1`."
        elif "stack overflow" in question.lower() or "limit" in question.lower():
            return "A **stack overflow** occurs because each recursive call requires memory to store its arguments and variables. This memory is stored in stack frames. \n\n" \
                   "Python has a default recursion limit of **1000 calls**. If your recursion goes deeper than that, Python stops it automatically. You can increase this using `sys.setrecursionlimit()`, but it is usually better to optimize your algorithm (or use loops) to prevent stack build-up."
                   
    # Generic fallback
    return f"Regarding your question *'{question}'* about **{concept}**:\n\n" \
           f"Here is an explanation tailored to your **{level}** level:\n\n" \
           f"1. **Core Concept Connection:** This relates directly to how state and variables are managed in the background.\n" \
           f"2. **Real-world Insight:** Think of it like reading the index of a book. Instead of reading the whole book again, you are zooming in on this specific page.\n" \
           f"3. **Practical Tip:** When implementing this, start by testing the simplest possible input (e.g. `None`, `0` or empty lists) to check how your logic behaves under basic inputs.\n\n" \
           f"Let me know if you would like me to show a code snippet or another analogy!"


