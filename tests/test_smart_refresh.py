"""
Tests for Smart Refresh Interface, Activities, and Cooldown Limits
"""

import time
import unittest

from smart_refresh.refresh_engine import (
    start_refresh,
    is_cooldown_active,
    check_fatigue_signals,
    select_refresh_activity,
    should_terminate_refresh,
    MAX_REFRESH_DURATION_SECONDS,
    DEFAULT_COOLDOWN_MINUTES
)
from smart_refresh.memory_game import get_memory_card_deck
from smart_refresh.guess_concept import get_guess_challenge
from smart_refresh.gk import get_gk_trivia
from smart_refresh.math_games import get_math_puzzle
from smart_refresh.english_games import get_word_puzzle
from smart_refresh.riddles import get_riddle
from smart_refresh.tongue_twisters import get_tongue_twister
from smart_refresh.relaxation import get_relaxation_activity
from smart_refresh.friendly_chat import get_friendly_chat_prompt, respond_to_user_message

class TestSmartRefresh(unittest.TestCase):
    
    def test_refresh_duration_capped_at_5_minutes(self):
        session = start_refresh()
        self.assertLessEqual(session["max_duration_seconds"], 300)
        self.assertEqual(session["max_duration_seconds"], MAX_REFRESH_DURATION_SECONDS)
        self.assertIn("resume_checkpoint", session)
        self.assertEqual(session["session_status"], "ready")

    def test_should_terminate_refresh_guardrail(self):
        # 300 seconds is the limit
        self.assertTrue(should_terminate_refresh(300))
        self.assertTrue(should_terminate_refresh(301))
        self.assertFalse(should_terminate_refresh(299))
        self.assertFalse(should_terminate_refresh(0))

    def test_cooldown_logic(self):
        # No previous refresh
        self.assertFalse(is_cooldown_active(None))
        
        # Freshly completed refresh (within 30 minutes)
        now = time.time()
        self.assertTrue(is_cooldown_active(now, cooldown_minutes=30))
        
        # Over 30 minutes ago
        past = now - (31 * 60)
        self.assertFalse(is_cooldown_active(past, cooldown_minutes=30))
        
        # Test start_refresh during active cooldown
        cooldown_session = start_refresh(last_refresh_timestamp=now, cooldown_minutes=30)
        self.assertEqual(cooldown_session["session_status"], "cooldown")
        self.assertGreater(cooldown_session["cooldown_remaining_seconds"], 0)
        self.assertIsNone(cooldown_session["recommended_activity"])

    def test_check_fatigue_signals(self):
        # High study duration
        self.assertTrue(check_fatigue_signals({"study_duration_minutes": 50}))
        
        # Error streak
        self.assertTrue(check_fatigue_signals({"consecutive_errors": 3}))
        
        # High response latency
        self.assertTrue(check_fatigue_signals({"response_latency_seconds": 125}))
        
        # User self-reported fatigue
        self.assertTrue(check_fatigue_signals({"user_reported_fatigue": True}))
        
        # Repeated hints
        self.assertTrue(check_fatigue_signals({"repeated_hints": 3}))
        
        # Skipped questions
        self.assertTrue(check_fatigue_signals({"skipped_questions": 4}))
        
        # Performance decline
        self.assertTrue(check_fatigue_signals({"performance_decline": True}))
        
        # Normal state
        normal_state = {
            "study_duration_minutes": 20,
            "consecutive_errors": 1,
            "response_latency_seconds": 30,
            "repeated_hints": 0,
            "skipped_questions": 1,
            "performance_decline": False,
            "user_reported_fatigue": False
        }
        self.assertFalse(check_fatigue_signals(normal_state))

    def test_select_refresh_activity(self):
        # 1. Exhaustion -> Relaxation or Friendly Chat
        profile = {"user_reported_fatigue": True}
        context = {}
        signals = {"exhaustion_level": "high"}
        act = select_refresh_activity(profile, context, signals)
        self.assertIn(act, ["relaxation", "friendly_chat"])
        
        # 2. Struggled concept -> Guess the concept
        profile = {"struggled_concepts": ["recursion"]}
        context = {}
        signals = {}
        act = select_refresh_activity(profile, context, signals)
        self.assertEqual(act, "guess_concept")
        
        # 3. Long technical session -> Memory Cards
        profile = {}
        context = {"is_technical": True}
        signals = {"study_duration_minutes": 35}
        act = select_refresh_activity(profile, context, signals)
        self.assertEqual(act, "memory_game")
        
        # 4. Default general fun
        profile = {}
        context = {}
        signals = {}
        act = select_refresh_activity(profile, context, signals)
        self.assertIn(act, ["gk", "math_games", "riddles", "english_games", "tongue_twisters"])

    def test_memory_game_payload(self):
        deck = get_memory_card_deck("general_cs", limit=3)
        self.assertIsInstance(deck, list)
        self.assertEqual(len(deck), 3)
        for card in deck:
            self.assertIn("id", card)
            self.assertIn("card_a", card)
            self.assertIn("card_b", card)
            
        # Test default/invalid fallback
        deck_fallback = get_memory_card_deck("invalid_topic")
        self.assertTrue(len(deck_fallback) > 0)

    def test_guess_concept_payload(self):
        challenge = get_guess_challenge("recursion")
        self.assertEqual(challenge["concept_id"], "recursion")
        self.assertEqual(len(challenge["hints"]), 3)
        self.assertEqual(challenge["answer"], "Recursion")
        
        # Test random fallback
        any_challenge = get_guess_challenge()
        self.assertIn("concept_id", any_challenge)
        self.assertIn("hints", any_challenge)
        self.assertIn("answer", any_challenge)

    def test_gk_payload(self):
        trivia = get_gk_trivia(limit=1)
        self.assertIsInstance(trivia, list)
        self.assertEqual(len(trivia), 1)
        q = trivia[0]
        self.assertIn("question", q)
        self.assertIn("options", q)
        self.assertIn("answer", q)
        self.assertIn(q["answer"], q["options"])

    def test_math_games_payload(self):
        puzzle = get_math_puzzle()
        self.assertIn("puzzle", puzzle)
        self.assertIn("options", puzzle)
        self.assertIn("answer", puzzle)
        self.assertIn("explanation", puzzle)

    def test_english_games_payload(self):
        puzzle = get_word_puzzle()
        self.assertIn("type", puzzle)
        self.assertIn("hint", puzzle)
        self.assertIn("answer", puzzle)

    def test_riddles_payload(self):
        riddle = get_riddle()
        self.assertIn("riddle", riddle)
        self.assertIn("hint", riddle)
        self.assertIn("answer", riddle)
        self.assertIn("explanation", riddle)

    def test_tongue_twisters_payload(self):
        twister = get_tongue_twister()
        self.assertIsInstance(twister, str)
        self.assertGreater(len(twister), 0)

    def test_relaxation_payload(self):
        activity = get_relaxation_activity("Box Breathing")
        self.assertEqual(activity["title"], "Box Breathing Reset")
        self.assertIn("steps", activity)
        self.assertGreater(len(activity["steps"]), 0)
        
        # Test default fallback
        any_activity = get_relaxation_activity()
        self.assertIn("title", any_activity)
        self.assertIn("steps", any_activity)

    def test_friendly_chat_payload(self):
        prompt = get_friendly_chat_prompt("Alice")
        self.assertIn("Alice", prompt)
        
        # Test simple encouragement response keywords
        res_tired = respond_to_user_message("I am so tired", "Bob")
        self.assertIn("Bob", res_tired)
        self.assertIn("breath", res_tired.lower())
        
        res_stressed = respond_to_user_message("It is too hard", "Bob")
        self.assertIn("progress", res_stressed.lower())
        
        res_bored = respond_to_user_message("feeling bored", "Bob")
        self.assertIn("focus", res_bored.lower())
        
        res_default = respond_to_user_message("What is going on?", "Bob")
        self.assertIn("fresh mind", res_default.lower())

if __name__ == "__main__":
    unittest.main()

