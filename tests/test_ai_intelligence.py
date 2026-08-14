"""
Comprehensive Unit and Functional Tests for AI Core Subsystem
Owner: Member 1 (Team Lead / AI & ML)

Tests all required AI capabilities:
- Beginner, Intermediate, Advanced, and Unknown level explanations
- Structured learning output format (analogy, technical, practical, check question)
- 'Still confused' feedback dynamic strategy pivoting
- Dynamic topic mastery calculation and knowledge level estimation
- Lightweight misconception detection with confidence calibration
- Prerequisite-aware and progression-aware recommendations
- Smart Refresh fatigue evaluation, recommendations, and 30-minute cooldown
"""

import unittest
from datetime import datetime, timedelta
from models.schemas import (
    LearnerProfile,
    ConceptExplanation,
    UnderstandingCheck,
    TopicMastery,
    FeedbackType,
    RefreshDecision,
    MisconceptionResult,
    RecommendationResult
)
from ai.teaching_engine import explain_concept
from ai.learner_profile import LearnerProfileManager, update_mastery
from ai.feedback_handler import process_feedback
from ai.misconception import detect_misconceptions
from ai.recommendations import get_learning_recommendation
from ai.refresh_decision import (
    should_offer_refresh,
    request_manual_refresh,
    calculate_fatigue_score
)


class TestAITeachingEngine(unittest.TestCase):
    """Tests for the AI Teaching Engine."""

    def test_beginner_explanation_structure(self):
        """Test explanation generation tailored for beginner level."""
        profile = LearnerProfileManager.create_profile("user_beginner", onboarded_level="beginner")
        result = explain_concept("Recursion", profile)

        self.assertIsInstance(result, ConceptExplanation)
        self.assertEqual(result.concept.lower(), "recursion")
        self.assertTrue(len(result.real_world_analogy) > 10, "Analogy must be present")
        self.assertTrue(len(result.simple_explanation) > 10, "Simple explanation must be present")
        self.assertTrue(len(result.technical_explanation) > 10, "Technical explanation must be present")
        self.assertTrue(len(result.practical_application) > 5, "Practical application must be present")
        self.assertTrue(len(result.example_code_or_visual) > 5, "Example/code must be present")
        
        # Verify Understanding Check
        self.assertIsInstance(result.understanding_check, UnderstandingCheck)
        self.assertTrue(len(result.understanding_check.question) > 5)
        self.assertTrue(len(result.understanding_check.options) >= 2)
        self.assertTrue(len(result.understanding_check.correct_answer) > 0)
        self.assertTrue(len(result.understanding_check.explanation) > 0)

    def test_intermediate_explanation(self):
        """Test explanation generation for intermediate level."""
        profile = LearnerProfileManager.create_profile("user_intermediate", onboarded_level="intermediate")
        result = explain_concept("Binary Search", profile)
        self.assertIsInstance(result, ConceptExplanation)
        self.assertEqual(result.difficulty, "intermediate")

    def test_advanced_explanation(self):
        """Test explanation generation for advanced level."""
        profile = LearnerProfileManager.create_profile("user_adv", onboarded_level="advanced")
        result = explain_concept("Hash Table", profile)
        self.assertIsInstance(result, ConceptExplanation)
        self.assertEqual(result.difficulty, "advanced")

    def test_unknown_learner_level_does_not_assume(self):
        """Test that unknown/undetermined level produces balanced explanation without crashing."""
        profile = LearnerProfileManager.create_profile("user_fresh", onboarded_level="let_ai_determine")
        self.assertEqual(profile.estimated_level, "undetermined")
        
        result = explain_concept("Binary Search", profile)
        self.assertIsInstance(result, ConceptExplanation)
        self.assertIsNotNone(result.real_world_analogy)
        self.assertIsNotNone(result.technical_explanation)

    def test_dictionary_serialization(self):
        """Test that .to_dict() serializes completely for frontend/database consumers."""
        result = explain_concept("Recursion")
        dict_data = result.to_dict()
        self.assertIsInstance(dict_data, dict)
        self.assertIn("real_world_analogy", dict_data)
        self.assertIn("understanding_check", dict_data)
        self.assertIsInstance(dict_data["understanding_check"], dict)


class TestFeedbackAndStrategyPivot(unittest.TestCase):
    """Tests for Understanding Feedback and Pedagogical Strategy Pivots."""

    def test_still_confused_triggers_strategy_pivot(self):
        """When learner is 'still confused', AI changes teaching strategy rather than repeating."""
        profile = LearnerProfileManager.create_profile("user_confused", onboarded_level="beginner")
        initial_exp = explain_concept("Recursion", profile)
        self.assertEqual(initial_exp.style_used, "analogy_first")

        # Learner clicks 'Still confused'
        feedback_res = process_feedback(
            feedback="still_confused",
            concept="Recursion",
            learner_profile=profile,
            previous_explanation=initial_exp
        )

        self.assertTrue(feedback_res["strategy_changed"])
        self.assertNotEqual(feedback_res["new_style"], "analogy_first")
        self.assertIsNotNone(feedback_res["alternative_explanation"])
        self.assertIn(feedback_res["new_style"], [
            "super_simple", "step_by_step", "visual", "practical_code", "technical_deep_dive"
        ])

    def test_got_it_feedback_records_success(self):
        """Positive feedback is recorded and updates metrics."""
        profile = LearnerProfileManager.create_profile("user_success")
        res = process_feedback("got_it", "Binary Search", profile)
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["strategy_changed"])
        self.assertTrue(len(profile.feedback_history) == 1)
        self.assertEqual(profile.feedback_history[0]["feedback_type"], "got_it")


class TestLearnerProfileAndMastery(unittest.TestCase):
    """Tests for Learner Profile, Dynamic Mastery, and Knowledge Estimation."""

    def test_topic_mastery_incremental_updates(self):
        """Mastery increases smoothly on correct answers and decreases on wrong answers."""
        profile = LearnerProfileManager.create_profile("user_mastery_test")
        
        # 1st correct answer
        mastery1 = LearnerProfileManager.update_mastery(profile, "Recursion", is_correct=True)
        score_after_first = mastery1.score
        self.assertGreater(score_after_first, 0.5)
        self.assertEqual(mastery1.correct_count, 1)
        self.assertEqual(mastery1.attempts_count, 1)

        # 2nd correct answer -> should move towards mastered
        mastery2 = LearnerProfileManager.update_mastery(profile, "Recursion", is_correct=True)
        score_after_second = mastery2.score
        self.assertGreater(score_after_second, score_after_first)

        # 3rd incorrect answer -> should decrease score
        mastery3 = LearnerProfileManager.update_mastery(profile, "Recursion", is_correct=False)
        score_after_third = mastery3.score
        self.assertLess(score_after_third, score_after_second)

    def test_dynamic_knowledge_level_progression(self):
        """Profile gradually graduates from beginner to advanced as mastery accumulates."""
        profile = LearnerProfileManager.create_profile("user_learner", onboarded_level="let_ai_determine")
        self.assertEqual(profile.estimated_level, "undetermined")

        # Simulate mastering 3 topics
        for topic in ["Python Basics", "Functions", "Recursion"]:
            for _ in range(4):
                LearnerProfileManager.update_mastery(profile, topic, is_correct=True, difficulty="intermediate")
            LearnerProfileManager.record_feedback(profile, "got_it", topic)

        level = LearnerProfileManager.estimate_knowledge_level(profile)
        self.assertIn(level, ["intermediate", "advanced"])
        self.assertGreater(profile.level_confidence, 0.5)


class TestMisconceptionDetection(unittest.TestCase):
    """Tests for Lightweight Misconception Detection."""

    def test_recursion_missing_base_case_misconception(self):
        """Detects misconception that recursion is an infinite loop."""
        res = detect_misconceptions(
            concept="Recursion",
            student_answer="Recursion always runs forever in a loop because it keeps calling itself."
        )
        self.assertTrue(res.has_misconception)
        self.assertIn("Base Case", res.explanation)
        self.assertGreaterEqual(res.confidence, 0.70)

    def test_binary_search_unsorted_array_misconception(self):
        """Detects misconception that binary search works on any unsorted array."""
        res = detect_misconceptions(
            concept="Binary Search",
            student_answer="I can run binary search on any list even if it is completely unsorted."
        )
        self.assertTrue(res.has_misconception)
        self.assertIn("sorted", res.explanation.lower())
        self.assertGreaterEqual(res.confidence, 0.80)

    def test_correct_response_has_no_misconception(self):
        """Accurate response does not trigger a false positive misconception."""
        res = detect_misconceptions(
            concept="Binary Search",
            student_answer="Binary search requires a sorted collection and divides the search space in half at each step."
        )
        self.assertFalse(res.has_misconception)


class TestLearningRecommendations(unittest.TestCase):
    """Tests for Prerequisite-Aware and Progression-Aware Recommendations."""

    def test_recommends_prerequisite_when_weak(self):
        """Example from prompt: Functions mastered, Recursion weak -> strengthen Recursion before Trees."""
        profile = LearnerProfileManager.create_profile("user_rec_test")
        
        # Python Basics & Functions mastered
        for _ in range(3):
            LearnerProfileManager.update_mastery(profile, "python basics", is_correct=True)
            LearnerProfileManager.update_mastery(profile, "functions", is_correct=True)

        # Recursion is weak
        LearnerProfileManager.update_mastery(profile, "recursion", is_correct=False)
        LearnerProfileManager.update_mastery(profile, "recursion", is_correct=False)

        # Asking for next recommendation from Recursion
        rec = get_learning_recommendation(profile, current_topic="recursion")
        self.assertEqual(rec.suggested_next_topic.lower(), "recursion")
        self.assertIn("recursion", rec.reason.lower())

    def test_recommends_progression_when_mastered(self):
        """When Recursion is mastered, recommend Tree Traversals or Divide and Conquer."""
        profile = LearnerProfileManager.create_profile("user_mastered_test")
        for _ in range(4):
            LearnerProfileManager.update_mastery(profile, "python basics", is_correct=True)
            LearnerProfileManager.update_mastery(profile, "functions", is_correct=True)
            LearnerProfileManager.update_mastery(profile, "recursion", is_correct=True)

        rec = get_learning_recommendation(profile, current_topic="recursion")
        self.assertIn(rec.suggested_next_topic.lower(), ["tree traversals", "divide and conquer", "dynamic programming"])


class TestSmartRefreshDecisionEngine(unittest.TestCase):
    """Tests for Cognitive Fatigue Estimation, Recommendations, and Cooldowns."""

    def test_recommends_break_on_high_fatigue(self):
        """Recommends break when session duration is long and error streak is high."""
        session_data = {
            "study_duration_minutes": 50,
            "consecutive_errors": 4,
            "latency_increasing": True,
            "self_reported_fatigue": False
        }
        decision = should_offer_refresh(session_data, refresh_history=[])
        self.assertTrue(decision.recommend_break)
        self.assertGreaterEqual(decision.fatigue_score, 0.60)
        self.assertFalse(decision.cooldown_active)
        self.assertIsNotNone(decision.suggested_activity)

    def test_does_not_recommend_break_when_fresh(self):
        """Does not recommend break when learner is fresh and performing well."""
        session_data = {
            "study_duration_minutes": 10,
            "consecutive_errors": 0,
            "latency_increasing": False,
            "self_reported_fatigue": False
        }
        decision = should_offer_refresh(session_data, refresh_history=[])
        self.assertFalse(decision.recommend_break)
        self.assertLess(decision.fatigue_score, 0.40)

    def test_refresh_cooldown_enforcement(self):
        """Enforces 30-minute cooldown if a break was taken 10 minutes ago."""
        recent_break_ts = (datetime.now() - timedelta(minutes=10)).isoformat()
        refresh_history = [
            {"activity_type": "memory_game", "created_at": recent_break_ts, "duration_seconds": 240}
        ]
        session_data = {
            "study_duration_minutes": 50,
            "consecutive_errors": 4
        }
        
        # Test with 30-minute cooldown
        decision = should_offer_refresh(session_data, refresh_history=refresh_history, cooldown_minutes=30.0)
        self.assertFalse(decision.recommend_break)
        self.assertTrue(decision.cooldown_active)
        self.assertGreater(decision.cooldown_remaining_minutes, 0.0)

    def test_manual_refresh_request(self):
        """User can always manually request a refresh."""
        decision = request_manual_refresh(session_data={}, refresh_history=[])
        self.assertTrue(decision.recommend_break)
        self.assertFalse(decision.cooldown_active)


if __name__ == "__main__":
    unittest.main()
