"""
Personalized Recommendation and Curriculum Progression Engine
Owner: Member 1 (Team Lead / AI & ML)

Responsibilities:
- Graph-based prerequisite analysis and next-topic sequencing.
- Detect weak topics and recommend remediation before advancing to dependent concepts.
- Example: If Functions is mastered but Recursion is weak, recommend strengthening Recursion
  prior to attempting Tree Traversals or Divide & Conquer.
"""

from typing import Dict, Any, Optional, List, Union
from models.schemas import RecommendationResult, LearnerProfile, TopicMastery
from ai.learner_profile import LearnerProfileManager

# Curriculum Dependency Graph: Topic -> {prerequisites, next_topics, default_difficulty}
CURRICULUM_GRAPH: Dict[str, Dict[str, Any]] = {
    "python basics": {
        "title": "Python Basics",
        "prerequisites": [],
        "next_topics": ["functions", "control flow"],
        "difficulty": "beginner"
    },
    "control flow": {
        "title": "Control Flow & Loops",
        "prerequisites": ["python basics"],
        "next_topics": ["functions", "arrays and lists"],
        "difficulty": "beginner"
    },
    "functions": {
        "title": "Functions & Scope",
        "prerequisites": ["python basics", "control flow"],
        "next_topics": ["recursion", "oop basics"],
        "difficulty": "beginner"
    },
    "recursion": {
        "title": "Recursion",
        "prerequisites": ["functions"],
        "next_topics": ["tree traversals", "divide and conquer", "dynamic programming"],
        "difficulty": "intermediate"
    },
    "arrays and lists": {
        "title": "Arrays and Lists",
        "prerequisites": ["python basics"],
        "next_topics": ["binary search", "hash table"],
        "difficulty": "beginner"
    },
    "binary search": {
        "title": "Binary Search",
        "prerequisites": ["arrays and lists", "control flow"],
        "next_topics": ["sorting algorithms", "binary search trees"],
        "difficulty": "intermediate"
    },
    "hash table": {
        "title": "Hash Table / Hash Map",
        "prerequisites": ["arrays and lists"],
        "next_topics": ["caching systems", "graph representations"],
        "difficulty": "intermediate"
    },
    "tree traversals": {
        "title": "Tree Traversals",
        "prerequisites": ["recursion", "arrays and lists"],
        "next_topics": ["binary search trees", "graph algorithms"],
        "difficulty": "intermediate"
    },
    "divide and conquer": {
        "title": "Divide and Conquer",
        "prerequisites": ["recursion"],
        "next_topics": ["merge sort", "quick sort"],
        "difficulty": "advanced"
    },
    "dynamic programming": {
        "title": "Dynamic Programming",
        "prerequisites": ["recursion", "arrays and lists"],
        "next_topics": ["memoization & tabulation", "knapsack problem"],
        "difficulty": "advanced"
    }
}


def _get_topic_score(profile: LearnerProfile, topic_key: str) -> float:
    """Retrieve current mastery score for a topic (default 0.0)."""
    mastery = profile.topic_mastery.get(topic_key)
    if mastery:
        return mastery.score
    return 0.0


def get_learning_recommendation(
    learner_profile: Optional[Union[LearnerProfile, Dict[str, Any]]] = None,
    current_topic: Optional[str] = None
) -> RecommendationResult:
    """
    Computes personalized next-topic recommendation based on knowledge graph and mastery profile.
    
    Args:
        learner_profile: LearnerProfile object or dictionary.
        current_topic: Optional current concept studied.
        
    Returns:
        RecommendationResult: Next recommended step with rationale.
    """
    if isinstance(learner_profile, LearnerProfile):
        profile = learner_profile
    elif isinstance(learner_profile, dict) and "user_id" in learner_profile:
        profile = LearnerProfileManager.get_or_create_profile(learner_profile["user_id"])
    else:
        profile = LearnerProfileManager.get_or_create_profile("guest_user")

    # Identify all currently weak topics in the learner's profile (< 0.55 score)
    weak_topics = []
    for key, mastery in profile.topic_mastery.items():
        if mastery.score < 0.55:
            weak_topics.append(mastery.topic)

    curr_key = current_topic.lower().strip() if current_topic else None

    # Case 1: Current topic is provided and exists in Curriculum Graph
    if curr_key and curr_key in CURRICULUM_GRAPH:
        node = CURRICULUM_GRAPH[curr_key]
        curr_score = _get_topic_score(profile, curr_key)

        # Check if any prerequisites are missing or weak
        unmet_prereqs = []
        for prereq in node["prerequisites"]:
            prereq_score = _get_topic_score(profile, prereq)
            if prereq_score < 0.55:
                prereq_title = CURRICULUM_GRAPH.get(prereq, {}).get("title", prereq.title())
                unmet_prereqs.append(prereq_title)

        if unmet_prereqs:
            return RecommendationResult(
                current_topic=node["title"],
                suggested_next_topic=unmet_prereqs[0],
                recommended_difficulty="beginner",
                reason=(
                    f"To build a strong foundation for '{node['title']}', we recommend revisiting prerequisite "
                    f"topic '{unmet_prereqs[0]}' first."
                ),
                weak_topics_to_review=weak_topics,
                prerequisites_to_revisit=unmet_prereqs,
                confidence=0.92
            )

        # If current topic itself is struggling or not mastered (< 0.60)
        if curr_score < 0.60:
            return RecommendationResult(
                current_topic=node["title"],
                suggested_next_topic=node["title"],
                recommended_difficulty=node["difficulty"],
                reason=(
                    f"Your mastery on '{node['title']}' is currently {int(curr_score * 100)}%. "
                    "We recommend reinforcing this concept with alternative analogies and quizzes before advancing."
                ),
                weak_topics_to_review=weak_topics,
                prerequisites_to_revisit=[],
                confidence=0.88
            )

        # If current topic is mastered (>= 0.60), recommend next logical topic in graph
        for next_topic_key in node["next_topics"]:
            next_score = _get_topic_score(profile, next_topic_key)
            if next_score < 0.70:
                next_title = CURRICULUM_GRAPH.get(next_topic_key, {}).get("title", next_topic_key.title())
                next_diff = CURRICULUM_GRAPH.get(next_topic_key, {}).get("difficulty", "intermediate")
                return RecommendationResult(
                    current_topic=node["title"],
                    suggested_next_topic=next_title,
                    recommended_difficulty=next_diff,
                    reason=(
                        f"Great progress! You have mastered '{node['title']}'. The ideal next progression is '{next_title}'."
                    ),
                    weak_topics_to_review=weak_topics,
                    prerequisites_to_revisit=[],
                    confidence=0.90
                )

    # Case 2: If learner has identified weak topics, prioritize the weakest topic
    if weak_topics:
        weakest_topic = weak_topics[0]
        return RecommendationResult(
            current_topic=current_topic,
            suggested_next_topic=weakest_topic,
            recommended_difficulty="beginner",
            reason=f"Let's strengthen your understanding in '{weakest_topic}' to reinforce your conceptual foundation.",
            weak_topics_to_review=weak_topics,
            prerequisites_to_revisit=[],
            confidence=0.85
        )

    # Case 3: Default progressive entry point
    return RecommendationResult(
        current_topic=current_topic,
        suggested_next_topic="Recursion",
        recommended_difficulty=profile.estimated_level if profile.estimated_level != "undetermined" else "beginner",
        reason="Explore core problem decomposition techniques with Recursion.",
        weak_topics_to_review=[],
        prerequisites_to_revisit=[],
        confidence=0.80
    )


def get_next_recommendations(user_id: str, current_topic: str) -> List[str]:
    """Legacy helper returning simple list of recommended topic titles."""
    profile = LearnerProfileManager.get_or_create_profile(user_id)
    rec = get_learning_recommendation(profile, current_topic)
    return [rec.suggested_next_topic] + rec.weak_topics_to_review
