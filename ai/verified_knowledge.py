"""
Verified Ground-Truth Knowledge Base for ConceptBridge AI
Owner: Member 1 (Team Lead / AI & ML)

Core Architecture Rule:
Accuracy is prioritized over creativity. The AI simplifies verified domain knowledge
rather than hallucinating technical definitions, properties, or mathematical formulas.
"""

from typing import Dict, Any, Optional

VERIFIED_KNOWLEDGE_CATALOG: Dict[str, Dict[str, Any]] = {
    "graph coloring": {
        "concept": "Graph Coloring",
        "scientific_definition": (
            "In graph theory, graph coloring is an assignment of labels (called 'colors') to elements of a graph "
            "subject to certain constraints. In vertex coloring, colors are assigned to vertices such that no two adjacent "
            "vertices connected by an edge share the same color. The minimum number of colors needed to color a graph G is "
            "called its chromatic number, denoted as χ(G)."
        ),
        "real_world_analogy": (
            "Think of scheduling university final exams to avoid student conflicts:\n"
            "• Each Course Exam is a Vertex (node).\n"
            "• If at least one student is enrolled in both Exam A and Exam B, we draw a Conflict Edge between them.\n"
            "• Each Available Time Slot is a Color.\n"
            "• The Rule: Two connected exams cannot happen in the same time slot (they must have different colors).\n"
            "The minimum number of exam time slots needed without scheduling conflicts is the Chromatic Number χ(G)."
        ),
        "simple_explanation": (
            "Graph coloring is like coloring a map or schedule so that neighbors never have the same color. "
            "If two circles are connected by a line, you MUST color them differently. The challenge is finding "
            "the fewest possible colors needed to color the whole graph without any neighboring conflicts."
        ),
        "technical_explanation": (
            "Formally, a proper vertex coloring of an undirected graph G = (V, E) is a function c: V → {1, 2, ..., k} "
            "such that for all edges (u, v) ∈ E, c(u) ≠ c(v). Finding the chromatic number χ(G) or deciding if a graph "
            "is k-colorable for k ≥ 3 is NP-complete. For planar graphs, the Four Color Theorem proves that χ(G) ≤ 4. "
            "Standard heuristics include greedy coloring (Welsh-Powell, DSatur) and backtracking with constraint satisfaction."
        ),
        "practical_application": (
            "1. Register Allocation in Compilers: Assigning limited CPU registers to variables that are live simultaneously.\n"
            "2. Frequency Assignment in Wireless Networks: Assigning radio frequencies to nearby cellular towers without interference.\n"
            "3. University Exam & Sports Timetabling: Scheduling events without shared participant conflicts.\n"
            "4. Sudoku Puzzles: Sudoku is an exact instance of 9-coloring a graph with 81 vertices and 810 constraint edges."
        ),
        "example_code_or_visual": (
            "# Greedy Graph Coloring in Python\n"
            "def greedy_graph_coloring(graph: dict[str, list[str]]) -> dict[str, int]:\n"
            "    color_assignment = {}\n"
            "    for vertex in graph:\n"
            "        # Find colors used by adjacent neighbors\n"
            "        neighbor_colors = {color_assignment[neighbor] for neighbor in graph[vertex] if neighbor in color_assignment}\n"
            "        # Assign lowest available color\n"
            "        color = 0\n"
            "        while color in neighbor_colors:\n"
            "            color += 1\n"
            "        color_assignment[vertex] = color\n"
            "    return color_assignment\n\n"
            "# Example: Triangle Graph (K3)\n"
            "graph = {'A': ['B', 'C'], 'B': ['A', 'C'], 'C': ['A', 'B']}\n"
            "print(greedy_graph_coloring(graph))  # Outputs: {'A': 0, 'B': 1, 'C': 2} -> Needs 3 colors"
        ),
        "diagram_type": "graphviz",
        "diagram_code": (
            "graph GraphColoring {\n"
            "  bgcolor=\"transparent\";\n"
            "  node [style=filled, fontcolor=white, fontname=\"Helvetica\", shape=circle, width=0.8];\n"
            "  edge [color=\"#888888\", penwidth=2];\n"
            "  \n"
            "  A [fillcolor=\"#EF4444\", label=\"Task A\\n(Red)\"];\n"
            "  B [fillcolor=\"#3B82F6\", label=\"Task B\\n(Blue)\"];\n"
            "  C [fillcolor=\"#10B981\", label=\"Task C\\n(Green)\"];\n"
            "  D [fillcolor=\"#EF4444\", label=\"Task D\\n(Red)\"];\n"
            "  \n"
            "  A -- B [label=\"conflict\"];\n"
            "  A -- C [label=\"conflict\"];\n"
            "  B -- C [label=\"conflict\"];\n"
            "  B -- D [label=\"conflict\"];\n"
            "  C -- D [label=\"conflict\"];\n"
            "}"
        ),
        "diagram_caption": "Vertex Coloring on a 4-node graph: Adjacent vertices have different colors (Chromatic Number χ = 3).",
        "understanding_check": {
            "question": "In vertex graph coloring, what is the fundamental rule that every valid coloring must satisfy?",
            "options": [
                "A) Every vertex in the graph must have a unique color.",
                "B) No two vertices connected by an edge can have the same color.",
                "C) The number of colors must equal the number of edges.",
                "D) Edges must have the same color as their starting vertex."
            ],
            "correct_answer": "B) No two vertices connected by an edge can have the same color.",
            "explanation": "Proper vertex coloring requires that adjacent vertices (connected by an edge) receive distinct colors.",
            "concept_tested": "Vertex coloring adjacency constraint"
        },
        "difficulty": "intermediate",
        "confidence": 0.98,
        "key_takeaways": [
            "Rule: Adjacent vertices (neighbors sharing an edge) must have different colors.",
            "Chromatic number χ(G) is the minimal number of colors needed.",
            "Used heavily in compiler register allocation, timetabling, and frequency assignments."
        ]
    },
    "recursion": {
        "concept": "Recursion",
        "scientific_definition": (
            "In computer science and mathematics, recursion is a method of solving computational problems where a function "
            "calls itself directly or indirectly to solve smaller instances of the same problem, terminating at one or more base cases."
        ),
        "real_world_analogy": (
            "Think of looking up a word in a physical dictionary where the definition contains another word you don't know:\n"
            "1. You look up 'Gargantuan' -> Dictionary says: 'See Colossal'.\n"
            "2. You bookmark 'Gargantuan' and look up 'Colossal' -> Dictionary says: 'See Enormous'.\n"
            "3. You bookmark 'Colossal' and look up 'Enormous' -> Dictionary says: 'Extremely Large' (Base Case reached!).\n"
            "4. Now you return backward through your bookmarks: 'Enormous' means extremely large → so 'Colossal' means extremely large → so 'Gargantuan' means extremely large."
        ),
        "simple_explanation": (
            "Recursion is when a function solves a big task by asking a smaller version of itself to do part of the work. "
            "Every recursive function MUST have a Base Case (a stopping rule that stops calling itself) so it doesn't run forever."
        ),
        "technical_explanation": (
            "Recursion is executed using the system Call Stack. Each function call allocates a new stack frame holding its local variables, "
            "parameters, and return address. When the base case evaluates to true, stack frames unwind in Last-In-First-Out (LIFO) order. "
            "If the base case is missing or recursion depth exceeds the stack limit, a StackOverflowError occurs. Space complexity is O(D) "
            "where D is maximum call depth unless tail-call optimization (TCO) is applied by the runtime."
        ),
        "practical_application": (
            "1. File System Navigation: Traversing nested folders and subfolders on your computer.\n"
            "2. Document Object Model (DOM): Parsing and rendering HTML tag hierarchies in browsers.\n"
            "3. JSON/XML Serializers: Parsing arbitrarily nested objects and arrays.\n"
            "4. Divide and Conquer: Merge Sort, Quick Sort, and Tree Search."
        ),
        "example_code_or_visual": (
            "def factorial(n: int) -> int:\n"
            "    # 1. Base Case (stopping rule)\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    # 2. Recursive Step (smaller problem)\n"
            "    return n * factorial(n - 1)\n\n"
            "# Call Stack for factorial(3):\n"
            "# factorial(3) -> pushes frame (3 * factorial(2))\n"
            "#   factorial(2) -> pushes frame (2 * factorial(1))\n"
            "#     factorial(1) -> hits Base Case, returns 1\n"
            "#   unwinds: 2 * 1 = 2\n"
            "# unwinds: 3 * 2 = 6"
        ),
        "diagram_type": "graphviz",
        "diagram_code": (
            "digraph CallStack {\n"
            "  bgcolor=\"transparent\";\n"
            "  node [fontname=\"Helvetica\", shape=record, style=filled, fillcolor=\"#1E293B\", fontcolor=\"#38BDF8\", color=\"#0284C7\"];\n"
            "  edge [color=\"#94A3B8\", fontcolor=\"#F1F5F9\", fontsize=10];\n"
            "  \n"
            "  f3 [label=\"{factorial(3) | n = 3 | waits for factorial(2)}\"];\n"
            "  f2 [label=\"{factorial(2) | n = 2 | waits for factorial(1)}\"];\n"
            "  f1 [label=\"{factorial(1) | n = 1 | BASE CASE: returns 1}\", fillcolor=\"#065F46\", fontcolor=\"#34D399\"];\n"
            "  \n"
            "  f3 -> f2 [label=\"calls\"];\n"
            "  f2 -> f1 [label=\"calls\"];\n"
            "  f1 -> f2 [label=\"returns 1\", style=dashed, color=\"#34D399\"];\n"
            "  f2 -> f3 [label=\"returns 2*1=2\", style=dashed, color=\"#34D399\"];\n"
            "}"
        ),
        "diagram_caption": "Call Stack trace of factorial(3) executing down to Base Case factorial(1) and unwinding return values.",
        "understanding_check": {
            "question": "Why does a recursive function cause a Stack Overflow error if it lacks a valid Base Case?",
            "options": [
                "A) The computer converts recursion into an infinite while loop that consumes 100% CPU.",
                "B) Stack frames keep getting pushed onto the call stack indefinitely until allocated memory is exhausted.",
                "C) The compiler refuses to assemble any code without a return statement.",
                "D) The variables become corrupted due to garbage collection failure."
            ],
            "correct_answer": "B) Stack frames keep getting pushed onto the call stack indefinitely until allocated memory is exhausted.",
            "explanation": "Each recursive call pushes a new frame to the call stack. Without a stopping base case, stack memory is completely filled.",
            "concept_tested": "Base case and call stack memory mechanics"
        },
        "difficulty": "beginner",
        "confidence": 0.98,
        "key_takeaways": [
            "Every recursive function requires: 1) Base Case (stopping rule), 2) Recursive Call (advancing toward base case).",
            "State is managed in stack frames on the system call stack in LIFO order.",
            "Essential for hierarchical trees, nested data formats (JSON/XML), and divide-and-conquer algorithms."
        ]
    },
    "binary search": {
        "concept": "Binary Search",
        "scientific_definition": (
            "Binary search is an efficient search algorithm that finds the position of a target value within a sorted array. "
            "It operates in O(log N) time by repeatedly dividing the search interval in half."
        ),
        "real_world_analogy": (
            "Searching for a word in a 1,000-page printed physical dictionary:\n"
            "• You don't scan page by page from page 1.\n"
            "• You open directly to the middle (page 500). If your word comes after alphabetically, you discard pages 1–499 completely.\n"
            "• You flip to the middle of the remaining section (page 750) and repeat.\n"
            "Because the dictionary is SORTED, each check eliminates 50% of all remaining pages."
        ),
        "simple_explanation": (
            "Binary Search finds an item in a SORTED list by always looking at the exact middle item. "
            "If your target is smaller, you throw away the entire right half; if larger, you throw away the left half. "
            "You find your answer in very few steps even in millions of items."
        ),
        "technical_explanation": (
            "Binary Search requires the random-access collection to be monotonically sorted. At each iteration, "
            "`mid = low + (high - low) // 2` is calculated to avoid 32-bit integer overflow. The search space [low, high] "
            "is reduced by setting `high = mid - 1` or `low = mid + 1`. Time complexity is O(log N) worst/average case, "
            "O(1) best case. Space complexity is O(1) auxiliary memory for the iterative implementation."
        ),
        "practical_application": (
            "1. Database B-Tree Indexing: Quickly locating row IDs on disk.\n"
            "2. Git Bisect: Automated binary search through git commits to find the exact commit that introduced a bug.\n"
            "3. Autocomplete / Typeahead: Prefix range searching in sorted dictionaries."
        ),
        "example_code_or_visual": (
            "def binary_search(arr: list[int], target: int) -> int:\n"
            "    low, high = 0, len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = low + (high - low) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1  # Not found"
        ),
        "diagram_type": "graphviz",
        "diagram_code": (
            "digraph BinarySearch {\n"
            "  bgcolor=\"transparent\";\n"
            "  node [fontname=\"Helvetica\", shape=record, style=filled, fillcolor=\"#1E293B\", fontcolor=\"#F1F5F9\"];\n"
            "  \n"
            "  step1 [label=\"Step 1: [2, 5, 8, 12, | {<m> 16} | , 23, 38, 56, 72] | mid=16 < target 56 → Discard Left Half\"];\n"
            "  step2 [label=\"Step 2: [23, | {<m> 38} | , 56, 72] | mid=38 < target 56 → Discard Left Half\"];\n"
            "  step3 [label=\"Step 3: [{<m> 56} | , 72] | mid=56 == target 56 → FOUND!\", fillcolor=\"#065F46\", fontcolor=\"#34D399\"];\n"
            "  \n"
            "  step1 -> step2 -> step3 [color=\"#38BDF8\"];\n"
            "}"
        ),
        "diagram_caption": "Binary search halving the search space at each step to find target 56 in O(log N) comparisons.",
        "understanding_check": {
            "question": "What is the non-negotiable prerequisite that must hold before executing Binary Search on an array?",
            "options": [
                "A) The array must contain distinct positive integers only.",
                "B) The array elements must be sorted in order.",
                "C) The array length must be an exact power of 2.",
                "D) The array must be implemented as a linked list."
            ],
            "correct_answer": "B) The array elements must be sorted in order.",
            "explanation": "Binary search relies on sorted order to guarantee which half of the collection can be safely discarded.",
            "concept_tested": "Sorted collection invariant"
        },
        "difficulty": "beginner",
        "confidence": 0.98,
        "key_takeaways": [
            "Requires a pre-sorted random-access collection.",
            "Time complexity: O(log N) — searches 1 million items in ~20 steps.",
            "Iterative space complexity: O(1) constant memory."
        ]
    },
    "database indexing": {
        "concept": "Database Indexing & B-Trees",
        "scientific_definition": (
            "A database index is a data structure (commonly a B-Tree or B+ Tree) that improves the speed of data retrieval "
            "operations on a database table at the cost of additional storage space and slower writes (INSERT, UPDATE, DELETE)."
        ),
        "real_world_analogy": (
            "Think of the Index at the back of a 1,000-page textbook:\n"
            "• Without an index: If you want to find where 'Quantum Computing' is mentioned, you have to read all 1,000 pages (Full Table Scan).\n"
            "• With an index: You flip to the back, look up 'Quantum Computing' alphabetically, and it points directly to page 412 (Index Seek)."
        ),
        "simple_explanation": (
            "An index is like a fast shortcut table. Instead of reading millions of rows one by one to find a customer, "
            "the database looks up the index tree and jumps straight to the exact row on disk."
        ),
        "technical_explanation": (
            "Relational database indexes typically organize keys in multi-way balanced search trees (B+ Trees). In a B+ Tree, "
            "all data records/pointers reside in leaf nodes, and leaf nodes are linked sequentially for fast range scans. "
            "Lookups take O(log_B N) disk I/O operations where B is the block branching factor (often 100+). While SELECT queries "
            "speed up by orders of magnitude, INSERT/UPDATE/DELETE operations incur overhead to maintain tree balance."
        ),
        "practical_application": (
            "1. Primary Key Lookups: `SELECT * FROM users WHERE user_id = 'usr_123'` runs in <1 millisecond.\n"
            "2. Composite Indexes: Speeding up multi-column filtering: `WHERE country = 'US' AND status = 'active'`.\n"
            "3. Foreign Key Joins: Accelerating relational joins between orders and customers."
        ),
        "example_code_or_visual": (
            "-- Creating an index in SQL\n"
            "CREATE INDEX idx_users_email ON users(email);\n\n"
            "-- Query now uses Index Seek instead of Full Table Scan\n"
            "EXPLAIN QUERY PLAN\n"
            "SELECT * FROM users WHERE email = 'alex@conceptbridge.dev';"
        ),
        "diagram_type": "graphviz",
        "diagram_code": (
            "digraph BTreeIndex {\n"
            "  bgcolor=\"transparent\";\n"
            "  node [fontname=\"Helvetica\", shape=record, style=filled, fillcolor=\"#1E293B\", fontcolor=\"#F1F5F9\"];\n"
            "  edge [color=\"#38BDF8\"];\n"
            "  \n"
            "  root [label=\"Root Node: [Key 50]\"];\n"
            "  left [label=\"Internal Node: [Keys 10, 30]\"];\n"
            "  right [label=\"Internal Node: [Keys 70, 90]\"];\n"
            "  \n"
            "  leaf1 [label=\"Leaf: [Row 10, Row 20]\", fillcolor=\"#065F46\", fontcolor=\"#34D399\"];\n"
            "  leaf2 [label=\"Leaf: [Row 30, Row 40]\", fillcolor=\"#065F46\", fontcolor=\"#34D399\"];\n"
            "  \n"
            "  root -> left [label=\"< 50\"];\n"
            "  root -> right [label=\"≥ 50\"];\n"
            "  left -> leaf1;\n"
            "  left -> leaf2;\n"
            "}"
        ),
        "diagram_caption": "B-Tree index structure enabling O(log N) tree navigation to target row records on disk.",
        "understanding_check": {
            "question": "What is the primary trade-off when creating multiple indexes on a high-write database table?",
            "options": [
                "A) Read queries will become significantly slower.",
                "B) Write operations (INSERT/UPDATE/DELETE) become slower and storage usage increases.",
                "C) The database is forced to delete historical log files.",
                "D) The table can no longer support foreign keys."
            ],
            "correct_answer": "B) Write operations (INSERT/UPDATE/DELETE) become slower and storage usage increases.",
            "explanation": "Every write operation must update not only the table data but also all B-Tree index structures on the table.",
            "concept_tested": "Index read/write trade-off"
        },
        "difficulty": "intermediate",
        "confidence": 0.98,
        "key_takeaways": [
            "Converts O(N) full table scans into O(log N) index lookups.",
            "B+ Trees store all leaf nodes linked for rapid range queries.",
            "Trade-off: Drastically speeds up reads, but adds write overhead and disk storage."
        ]
    },
    "api": {
        "concept": "API (Application Programming Interface)",
        "scientific_definition": (
            "An Application Programming Interface (API) is a set of defined rules, protocols, and data contracts that enables "
            "different software applications to communicate and exchange data securely without knowing each other's internal implementation."
        ),
        "real_world_analogy": (
            "Think of a waiter in a restaurant:\n"
            "• You are the Customer (Client App / Browser).\n"
            "• The Kitchen is the Database & Server (Backend).\n"
            "• The Menu is the API Specification (Endpoint List).\n"
            "• The Waiter is the API: You give the waiter your order (Request), the waiter delivers it to the kitchen, and brings back your prepared food (Response). You don't need to cook or know how the stove works."
        ),
        "simple_explanation": (
            "An API is a software messenger that lets two apps talk to each other. For example, a weather app on your phone uses an API "
            "to request current temperatures from national weather station servers."
        ),
        "technical_explanation": (
            "Web APIs commonly follow the REST (Representational State Transfer) architectural pattern over HTTP/HTTPS. "
            "They utilize standard HTTP methods (GET for retrieving, POST for creating, PUT/PATCH for updating, DELETE for removing), "
            "stateless communication, standard status codes (200 OK, 404 Not Found, 500 Server Error), and JSON serialization for payloads."
        ),
        "practical_application": (
            "1. Payment Gateways: Stripe/PayPal APIs processing credit card transactions in ecommerce stores.\n"
            "2. OAuth Login: 'Sign in with Google' / 'Sign in with GitHub'.\n"
            "3. Cloud AI APIs: Calling OpenAI, Gemini, or Claude endpoints."
        ),
        "example_code_or_visual": (
            "# Calling a REST API in Python\n"
            "import requests\n\n"
            "response = requests.get('https://api.github.com/users/octocat')\n"
            "if response.status_code == 200:\n"
            "    user_data = response.json()\n"
            "    print(f\"User: {user_data['name']}, Public Repos: {user_data['public_repos']}\")"
        ),
        "diagram_type": "graphviz",
        "diagram_code": (
            "digraph APIFlow {\n"
            "  bgcolor=\"transparent\";\n"
            "  rankdir=LR;\n"
            "  node [fontname=\"Helvetica\", shape=box, style=\"filled,rounded\", fillcolor=\"#1E293B\", fontcolor=\"#F1F5F9\"];\n"
            "  edge [fontname=\"Helvetica\", fontsize=10];\n"
            "  \n"
            "  client [label=\"Client App\\n(Browser/Mobile)\", fillcolor=\"#0F766E\", fontcolor=\"#5EEAD4\"];\n"
            "  api [label=\"REST API Gateway\\n(HTTP / JSON)\", fillcolor=\"#1E40AF\", fontcolor=\"#93C5FD\"];\n"
            "  server [label=\"Backend Server &\\nDatabase\", fillcolor=\"#374151\", fontcolor=\"#F3F4F6\"];\n"
            "  \n"
            "  client -> api [label=\"HTTP Request\\nGET /users/123\", color=\"#38BDF8\"];\n"
            "  api -> server [label=\"Queries DB\", color=\"#94A3B8\"];\n"
            "  server -> api [label=\"Raw Data\", color=\"#94A3B8\"];\n"
            "  api -> client [label=\"JSON Response\\n{ id: 123, name: 'Alex' }\", color=\"#34D399\"];\n"
            "}"
        ),
        "diagram_caption": "Client-Server interaction via REST API over HTTP with JSON payloads.",
        "understanding_check": {
            "question": "Which HTTP method should be used when a client wants to create a new user resource via an API?",
            "options": [
                "A) GET",
                "B) POST",
                "C) DELETE",
                "D) HEAD"
            ],
            "correct_answer": "B) POST",
            "explanation": "POST is the standard HTTP method designated for submitting data to create a new resource on the server.",
            "concept_tested": "HTTP request methods in REST APIs"
        },
        "difficulty": "beginner",
        "confidence": 0.98,
        "key_takeaways": [
            "Acts as a structured communication contract between software systems.",
            "REST APIs use HTTP methods (GET, POST, PUT, DELETE) and JSON data.",
            "Hides internal implementation details while exposing secure endpoints."
        ]
    }
}


def lookup_verified_knowledge(concept_query: str) -> Optional[Dict[str, Any]]:
    """
    Looks up verified, factually ground-truthed knowledge for a concept query.
    Returns structured data if verified match exists, or None.
    """
    clean = concept_query.strip().lower()
    for key, data in VERIFIED_KNOWLEDGE_CATALOG.items():
        if key in clean or clean in key:
            return dict(data)
        # Check alias synonyms
        if "graph" in clean and "color" in clean and key == "graph coloring":
            return dict(data)
        if "index" in clean and "db" in clean and key == "database indexing":
            return dict(data)
        if "rest" in clean and "api" in clean and key == "api":
            return dict(data)
    return None
