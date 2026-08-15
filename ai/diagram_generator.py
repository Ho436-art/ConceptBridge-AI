"""
Diagram Generator and Visualization Module for ConceptBridge AI
Owner: Member 1 (Team Lead / AI & ML)

Provides real, visual diagram specifications (Graphviz DOT, Mermaid, or Plotly/SVG)
for educational concepts, strictly avoiding fake code blocks pretending to be diagrams.
"""

from typing import Dict, Any, Optional, Tuple


def get_diagram_for_concept(concept_name: str) -> Tuple[Optional[str], Optional[str], str]:
    """
    Returns (diagram_type, diagram_code, caption) for a concept.
    
    Returns:
        diagram_type: 'graphviz', 'mermaid', 'none'
        diagram_code: string specification for rendering
        caption: explanatory label
    """
    clean = concept_name.lower().strip()

    # 1. Graph Coloring
    if "graph" in clean and "color" in clean:
        code = (
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
        )
        caption = "Graph Coloring: Adjacent vertices connected by an edge have different colors (Chromatic Number χ = 3)."
        return "graphviz", code, caption

    # 2. Recursion / Call Stack
    if "recursion" in clean or "call stack" in clean:
        code = (
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
        )
        caption = "Call Stack trace: function calls allocate stack frames down to the Base Case, then unwind return values in LIFO order."
        return "graphviz", code, caption

    # 3. Binary Search
    if "binary search" in clean:
        code = (
            "digraph BinarySearch {\n"
            "  bgcolor=\"transparent\";\n"
            "  node [fontname=\"Helvetica\", shape=record, style=filled, fillcolor=\"#1E293B\", fontcolor=\"#F1F5F9\"];\n"
            "  \n"
            "  step1 [label=\"Step 1: [2, 5, 8, 12, | {<m> 16} | , 23, 38, 56, 72] | mid=16 < target 56 → Discard Left Half\"];\n"
            "  step2 [label=\"Step 2: [23, | {<m> 38} | , 56, 72] | mid=38 < target 56 → Discard Left Half\"];\n"
            "  step3 [label=\"Step 3: [{<m> 56} | , 72] | mid=56 == target 56 → MATCH FOUND!\", fillcolor=\"#065F46\", fontcolor=\"#34D399\"];\n"
            "  \n"
            "  step1 -> step2 -> step3 [color=\"#38BDF8\", label=\"half space eliminated\"];\n"
            "}"
        )
        caption = "Binary Search Halving: Logarithmic O(log N) search eliminating half the sorted elements at each step."
        return "graphviz", code, caption

    # 4. Database Indexing / B-Trees
    if "index" in clean or "b-tree" in clean or "btree" in clean:
        code = (
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
        )
        caption = "B-Tree Database Index: Hierarchical structure enabling O(log N) tree navigation to target row records on disk."
        return "graphviz", code, caption

    # 5. REST API Architecture
    if "api" in clean or "rest" in clean:
        code = (
            "digraph APIFlow {\n"
            "  bgcolor=\"transparent\";\n"
            "  rankdir=LR;\n"
            "  node [fontname=\"Helvetica\", shape=box, style=\"filled,rounded\", fillcolor=\"#1E293B\", fontcolor=\"#F1F5F9\"];\n"
            "  edge [fontname=\"Helvetica\", fontsize=10];\n"
            "  \n"
            "  client [label=\"Client App\\n(Browser / Mobile)\", fillcolor=\"#0F766E\", fontcolor=\"#5EEAD4\"];\n"
            "  api [label=\"REST API Gateway\\n(HTTP / JSON)\", fillcolor=\"#1E40AF\", fontcolor=\"#93C5FD\"];\n"
            "  server [label=\"Backend Server &\\nDatabase\", fillcolor=\"#374151\", fontcolor=\"#F3F4F6\"];\n"
            "  \n"
            "  client -> api [label=\"HTTP GET /users/123\", color=\"#38BDF8\"];\n"
            "  api -> server [label=\"SQL Query\", color=\"#94A3B8\"];\n"
            "  server -> api [label=\"Record Data\", color=\"#94A3B8\"];\n"
            "  api -> client [label=\"JSON 200 OK\", color=\"#34D399\"];\n"
            "}"
        )
        caption = "Client-Server interaction via REST API over HTTP with JSON data payloads."
        return "graphviz", code, caption

    # If no verified visual model exists for this concept:
    return "none", None, "Diagram is not available for this concept."
