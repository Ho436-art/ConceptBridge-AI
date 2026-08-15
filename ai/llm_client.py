"""
LLM Client and Fallback Engine for ConceptBridge AI.
Owner: Member 1 (Team Lead / AI & ML)

Handles:
- Dynamic integration with OpenAI (GPT models) and Google Gemini when API keys are configured.
- Graceful, intelligent pedagogical knowledge fallback when running offline, during unit testing, or when keys are absent.
- Strict JSON response parsing and validation against ConceptExplanation schema.
"""

import os
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


# Built-in curated knowledge base for reliable fallback / test execution
CURATED_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "recursion": {
        "concept": "Recursion",
        "real_world_analogy": (
            "Think of Russian Matryoshka nesting dolls. To find the tiny prize inside the smallest doll, "
            "you open a big doll, which contains a slightly smaller doll, which contains an even smaller doll. "
            "You keep doing the exact same action (opening the doll) on a smaller version of the problem until you reach the "
            "solid wooden baby doll that cannot be opened (the Base Case). Once you reach the baby doll, you close them back up in reverse order."
        ),
        "simple_explanation": (
            "Recursion is simply a programming technique where a function solves a problem by calling itself with a smaller input. "
            "Every recursive function needs two critical parts: 1) A Base Case (the stopping rule that prevents an endless loop), "
            "and 2) A Recursive Step (calling itself to do a smaller piece of the work)."
        ),
        "technical_explanation": (
            "Under the hood, recursion relies on the Call Stack. Each recursive invocation creates a new stack frame containing local "
            "variables and the return instruction address. Execution pauses for the calling frame while the new child frame executes. "
            "When the base case evaluates to true, stack frames unwind in Last-In-First-Out (LIFO) order, returning intermediate values. "
            "Without a reachable base case or with excessive depth, the call stack exhausts available memory, resulting in a StackOverflowError."
        ),
        "practical_application": (
            "Recursion is widely used in production for traversing nested file directories on your computer, parsing JSON/XML data trees, "
            "navigating DOM hierarchies in web browsers, and evaluating decision trees in game AI (like chess engines)."
        ),
        "example_code_or_visual": (
            "# Recursive Factorial in Python\n"
            "def factorial(n: int) -> int:\n"
            "    # 1. Base Case: 0! or 1! is 1\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    # 2. Recursive Step: n * factorial(n - 1)\n"
            "    return n * factorial(n - 1)\n\n"
            "# Call Trace for factorial(3):\n"
            "# factorial(3) -> 3 * factorial(2)\n"
            "#                 factorial(2) -> 2 * factorial(1)\n"
            "#                                 factorial(1) -> 1 (Base Case hit!)\n"
            "# Unwinds: 3 * (2 * 1) = 6"
        ),
        "understanding_check": {
            "question": "What happens if a recursive function does NOT have a valid Base Case?",
            "options": [
                "A) The function will return 0 automatically.",
                "B) The function will call itself infinitely until a Stack Overflow error occurs.",
                "C) The compiler will convert the recursion into a while loop.",
                "D) The code will execute faster because it skips condition checks."
            ],
            "correct_answer": "B) The function will call itself infinitely until a Stack Overflow error occurs.",
            "explanation": "Without a base case, the stopping condition is never reached, continuously pushing new frames to the call stack until memory is exhausted.",
            "concept_tested": "Base Case and Call Stack limits"
        },
        "difficulty": "intermediate",
        "confidence": 0.95,
        "style_used": "analogy_first",
        "key_takeaways": [
            "Always define a base case first to avoid infinite recursion and stack overflow.",
            "Every recursive call must move closer to the base case.",
            "Recursion leverages the call stack (LIFO) to manage state across calls."
        ]
    },
    "binary search": {
        "concept": "Binary Search",
        "real_world_analogy": (
            "Imagine searching for the word 'Python' in a 1,000-page physical dictionary. You don't read page by page from page 1. "
            "Instead, you open the book right at the middle (page 500). You see words starting with 'M'. Since 'P' comes after 'M' alphabetically, "
            "you completely discard the first 500 pages and repeat the process on the remaining half. You repeat this half-splitting until you pinpoint 'Python' in just a few flips."
        ),
        "simple_explanation": (
            "Binary Search is a super-fast algorithm to find a target value in a SORTED list. Instead of checking every item one by one, "
            "it inspects the middle element. If the target is smaller, it searches the left half; if larger, the right half. "
            "Every single step cuts the remaining search space in half."
        ),
        "technical_explanation": (
            "Binary Search operates with O(log N) logarithmic time complexity and O(1) auxiliary space when implemented iteratively. "
            "At each step, mid is computed as `low + (high - low) // 2` to prevent 32-bit integer overflow. The search interval [low, high] "
            "is updated by setting `high = mid - 1` or `low = mid + 1`. The essential invariant is that the underlying array must be sorted."
        ),
        "practical_application": (
            "Binary Search powers database indexing (B-Trees / binary indexes), Git Bisect (for finding the exact commit that introduced a bug), "
            "and autocomplete search suggestions in search engines."
        ),
        "example_code_or_visual": (
            "def binary_search(arr: list[int], target: int) -> int:\n"
            "    low, high = 0, len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = low + (high - low) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid  # Found at index mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1   # Search right half\n"
            "        else:\n"
            "            high = mid - 1  # Search left half\n"
            "    return -1  # Not found"
        ),
        "understanding_check": {
            "question": "What is the mandatory prerequisite before you can perform a Binary Search on a collection?",
            "options": [
                "A) The collection must contain only distinct prime numbers.",
                "B) The collection must be sorted in ascending or descending order.",
                "C) The collection size must be an exact power of 2.",
                "D) The collection must be stored in a linked list."
            ],
            "correct_answer": "B) The collection must be sorted in ascending or descending order.",
            "explanation": "Binary search relies on order to determine whether to discard the left or right half. If unsorted, the algorithm cannot make that decision.",
            "concept_tested": "Sorted collection invariant"
        },
        "difficulty": "beginner",
        "confidence": 0.95,
        "style_used": "analogy_first",
        "key_takeaways": [
            "Prerequisite: The input array MUST be sorted.",
            "Time Complexity: O(log N) — can search 1 billion items in ~30 comparisons.",
            "Space Complexity: O(1) auxiliary memory."
        ]
    },
    "hash table": {
        "concept": "Hash Table / Hash Map",
        "real_world_analogy": (
            "Think of a coat check room at a theater. When you give the attendant your coat, they give you a claim ticket number (#42). "
            "When the show ends, you don't search through 500 coats; you show ticket #42, and the attendant walks straight to hook #42 to hand you your coat in one second."
        ),
        "simple_explanation": (
            "A Hash Table (or Dictionary/Map) is a data structure that stores Key-Value pairs. It gives you instant O(1) lookups by using a mathematical "
            "formula called a Hash Function that converts the key into an exact memory index."
        ),
        "technical_explanation": (
            "A hash function maps arbitrary key data to an integer array index `hash(key) % capacity`. When two distinct keys hash to the same bucket (collision), "
            "the system resolves it via Chaining (linked lists/trees in buckets) or Open Addressing (linear/quadratic probing). Under normal load factor (< 0.75), "
            "lookup, insertion, and deletion operate in O(1) average time, degrading to O(N) in worst-case pathological collision scenarios."
        ),
        "practical_application": (
            "Used in Python dictionaries, database caching layers (Redis, Memcached), session management in web frameworks, and duplicate detection."
        ),
        "example_code_or_visual": (
            "# Hash Table in Python (dict)\n"
            "student_grades = {'Alice': 95, 'Bob': 88, 'Charlie': 92}\n\n"
            "# O(1) Instant Lookup\n"
            "alice_grade = student_grades['Alice']  # Returns 95 directly without scanning Bob or Charlie"
        ),
        "understanding_check": {
            "question": "What is the average time complexity for searching a key in a well-distributed Hash Table?",
            "options": [
                "A) O(N)",
                "B) O(log N)",
                "C) O(1)",
                "D) O(N^2)"
            ],
            "correct_answer": "C) O(1)",
            "explanation": "A hash table uses direct index computation via the hash function to achieve O(1) constant time lookups on average.",
            "concept_tested": "Hash map average time complexity"
        },
        "difficulty": "intermediate",
        "confidence": 0.95,
        "style_used": "analogy_first",
        "key_takeaways": [
            "Stores key-value pairs with O(1) average lookup, insert, and delete.",
            "Hash collisions occur when different keys map to the same index.",
            "Underpins Python dictionaries and JavaScript objects."
        ]
    }
}


def _clean_json_string(raw_text: str) -> str:
    """Strip markdown code block markers and clean json string."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _normalize_json_payload(parsed: Dict[str, Any], fallback_concept: str = "") -> Dict[str, Any]:
    """Normalizes JSON dictionary fields to match ConceptExplanation schema."""
    concept = parsed.get("concept") or parsed.get("title") or fallback_concept.title() or "Concept"
    analogy = parsed.get("real_world_analogy") or parsed.get("analogy") or parsed.get("metaphor") or ""
    simple = parsed.get("simple_explanation") or parsed.get("explanation") or parsed.get("beginner_explanation") or ""
    technical = parsed.get("technical_explanation") or parsed.get("technical_mechanics") or parsed.get("technical_deep_dive") or ""
    practical = parsed.get("practical_application") or parsed.get("real_world_example") or parsed.get("practical_example") or ""
    code_or_vis = parsed.get("example_code_or_visual") or parsed.get("code_example") or parsed.get("visual_explanation") or "# Code / Example"
    
    check_raw = parsed.get("understanding_check") or {}
    if not isinstance(check_raw, dict):
        check_raw = {
            "question": f"What is the key principle behind {concept}?",
            "options": ["A) Correct conceptual mechanism", "B) False assumption", "C) Unrelated concept"],
            "correct_answer": "A) Correct conceptual mechanism",
            "explanation": "Reflects the core principle.",
            "concept_tested": concept
        }
    else:
        if not check_raw.get("question"):
            check_raw["question"] = f"What is the key rule of {concept}?"
        if not check_raw.get("options"):
            check_raw["options"] = ["A) Correct fundamental mechanism", "B) Common misconception", "C) Unrelated concept"]
        if not check_raw.get("correct_answer"):
            check_raw["correct_answer"] = check_raw["options"][0]
        if not check_raw.get("explanation"):
            check_raw["explanation"] = "Matches core conceptual mechanics."
        if not check_raw.get("concept_tested"):
            check_raw["concept_tested"] = concept

    return {
        "concept": concept,
        "real_world_analogy": analogy or f"Imagine {concept} in terms of everyday actions.",
        "simple_explanation": simple or f"{concept} is a fundamental topic.",
        "technical_explanation": technical or f"The underlying technical structure of {concept}.",
        "practical_application": practical or f"Where {concept} is applied in industry.",
        "example_code_or_visual": code_or_vis,
        "understanding_check": check_raw,
        "difficulty": parsed.get("difficulty", "beginner"),
        "confidence": float(parsed.get("confidence", 0.92)),
        "style_used": parsed.get("style_used", "analogy_first"),
        "key_takeaways": parsed.get("key_takeaways", [
            f"Understanding {concept} establishes strong foundations.",
            "Analyze operational trade-offs and boundary conditions."
        ]),
        "diagram_type": parsed.get("diagram_type", "none"),
        "diagram_code": parsed.get("diagram_code"),
        "diagram_caption": parsed.get("diagram_caption", "")
    }


def query_llm_json(prompt: str, system_prompt: str, fallback_concept: str = "", image_b64: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Calls official Groq SDK (Llama-3.3-70b-versatile / Llama-3.2-Vision) with OpenAI & Gemini fallbacks.
    Returns parsed normalized dictionary or None if API fails.
    """
    if os.getenv("TESTING", "").lower() == "true":
        return None

    # Reload .env at runtime to ensure latest keys are present
    load_dotenv(override=True)

    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    # 1. PRIMARY PROVIDER: Official Groq Python SDK
    if groq_key and len(groq_key) > 10:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            
            default_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
            
            if image_b64:
                model_to_use = "llama-3.2-11b-vision-preview"
                user_content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ]
            else:
                model_to_use = default_model
                user_content = prompt

            try:
                completion = client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                raw_content = completion.choices[0].message.content
                if raw_content:
                    parsed = json.loads(_clean_json_string(raw_content))
                    if isinstance(parsed, dict):
                        return _normalize_json_payload(parsed, fallback_concept=fallback_concept)
            except Exception as e_json:
                # If strict json validation fails, retry with standard text completion and clean JSON extraction
                completion = client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        {"role": "system", "content": system_prompt + "\nYou MUST return ONLY valid JSON."},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.3
                )
                raw_content = completion.choices[0].message.content
                if raw_content:
                    parsed = json.loads(_clean_json_string(raw_content))
                    if isinstance(parsed, dict):
                        return _normalize_json_payload(parsed, fallback_concept=fallback_concept)
        except Exception as e:
            # Report real error transparently to console
            print(f"[Groq SDK Error] {type(e).__name__}: {e}")

    # 2. SECONDARY: OpenAI if configured
    if openai_key and openai_key.startswith("sk-") and len(openai_key) > 20:
        try:
            import urllib.request
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}",
                "User-Agent": "ConceptBridge/1.0"
            }
            payload = {
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=4.0) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                content = res_data["choices"][0]["message"]["content"]
                parsed = json.loads(_clean_json_string(content))
                return _normalize_json_payload(parsed, fallback_concept=fallback_concept)
        except Exception as e:
            print(f"[OpenAI Error] {type(e).__name__}: {e}")

    # 3. TERTIARY: Gemini if key provided
    if gemini_key and len(gemini_key) > 10:
        import urllib.request
        candidate_models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]
        for model_name in candidate_models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                headers = {"Content-Type": "application/json", "User-Agent": "ConceptBridge/1.0"}
                payload = {
                    "contents": [
                        {"parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}\nRespond only in valid JSON."}]}
                    ]
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=4.0) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(_clean_json_string(content))
                    return _normalize_json_payload(parsed, fallback_concept=fallback_concept)
            except Exception:
                continue

    return None


def query_llm_text(prompt: str, system_prompt: str = "You are a helpful, empathetic learning assistant.") -> Optional[str]:
    """
    Direct text completion using official Groq SDK for chat, breaks, or short clarifications.
    """
    if os.getenv("TESTING", "").lower() == "true":
        return None

    load_dotenv(override=True)
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    
    if groq_key and len(groq_key) > 10:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            model_to_use = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
            completion = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            reply = completion.choices[0].message.content
            if reply:
                return reply.strip()
        except Exception as e:
            print(f"[Groq SDK Text Error] {type(e).__name__}: {e}")

    return None


def generate_structured_explanation_fallback(concept: str, level: str = "beginner", style: str = "analogy_first") -> Dict[str, Any]:
    """
    High-fidelity deterministic pedagogical fallback for offline/testing runs.
    Pulls from verified ground-truth knowledge bases.
    """
    clean_concept = concept.strip().lower()
    for key, data in CURATED_KNOWLEDGE_BASE.items():
        if key in clean_concept or clean_concept in key:
            res = dict(data)
            res["difficulty"] = level if level in ["beginner", "intermediate", "advanced"] else "beginner"
            res["style_used"] = style
            return res

    # Check verified ground-truth knowledge base
    from ai.verified_knowledge import lookup_verified_knowledge
    verified = lookup_verified_knowledge(concept)
    if verified:
        res = dict(verified)
        res["difficulty"] = level if level in ["beginner", "intermediate", "advanced"] else "beginner"
        res["style_used"] = style
        return res

    # Clear, honest message when unlisted concept cannot reach AI service
    title_concept = concept.strip().title() or "Concept"
    return {
        "concept": title_concept,
        "real_world_analogy": f"Could not connect to the live AI service to generate an analogy for {title_concept}.",
        "simple_explanation": (
            f"⚠️ ConceptBridge couldn't reach the AI service right now to explain '{title_concept}'. "
            "Please verify that your GROQ_API_KEY is configured in your .env file and that your internet connection is active."
        ),
        "technical_explanation": f"Live technical breakdown for '{title_concept}' requires an active AI connection.",
        "practical_application": "Real-world examples will be dynamically provided once the connection is established.",
        "example_code_or_visual": f"# Connect to Groq AI to view live code demonstrations for {title_concept}",
        "understanding_check": {
            "question": f"How do you enable AI-powered explanations for {title_concept}?",
            "options": [
                "A) Ensure GROQ_API_KEY is configured in .env",
                "B) Disable internet access",
                "C) Delete all database tables"
            ],
            "correct_answer": "A) Ensure GROQ_API_KEY is configured in .env",
            "explanation": "Setting a valid GROQ_API_KEY allows ConceptBridge AI to generate deep explanations.",
            "concept_tested": "AI Configuration"
        },
        "difficulty": level if level in ["beginner", "intermediate", "advanced"] else "beginner",
        "confidence": 0.0,
        "style_used": style,
        "key_takeaways": [
            "Check your local .env file for a valid GROQ_API_KEY.",
            "Ensure the Streamlit application has access to the internet."
        ]
    }
