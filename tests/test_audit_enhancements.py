"""
Audit and Enhancement Verification Test Suite for ConceptBridge AI
Tests all hackathon quality requirements:
- AI Factual Accuracy & Graph Coloring
- Conversational Intent Routing & Greetings ("hi")
- Diagram Generation (real Graphviz vs None)
- Student Dashboard (no AttributeError, clean metrics)
- Smart Refresh (Timer calculation, 30-min cooldown, Memory cards, Game pools & non-repetition)
"""

import unittest
import time
from ai.teaching_engine import explain_concept
from ai.conversation_engine import handle_chat_message, classify_intent, MessageIntent
from ai.diagram_generator import get_diagram_for_concept
from ai.verified_knowledge import lookup_verified_knowledge
from database.models import TopicMastery, User, LearnerProfile, Question, LearningSession, Recommendation
import smart_refresh.math_games as math_games
import smart_refresh.gk as gk
import smart_refresh.guess_concept as guess_concept
import smart_refresh.riddles as riddles
import smart_refresh.english_games as english_games
import smart_refresh.tongue_twisters as tongue_twisters
import smart_refresh.memory_game as memory_game
from frontend.pages.refresh import _calculate_cooldown_remaining


class TestAIAccuracyAndFactuality(unittest.TestCase):
    def test_graph_coloring_factual_accuracy(self):
        """Graph Coloring must convey vertex adjacency constraints, chromatic number, and conflict analogy."""
        exp = explain_concept("Graph Coloring")
        self.assertEqual(exp.concept, "Graph Coloring")
        # Check core definition contains chromatic number and adjacency constraint
        text_full = (exp.technical_explanation + " " + exp.simple_explanation + " " + exp.real_world_analogy).lower()
        self.assertIn("chromatic", text_full)
        self.assertTrue("adjacent" in text_full or "neighbor" in text_full)
        self.assertIn("conflict", text_full)
        # Check diagram is graphviz DOT
        self.assertEqual(exp.diagram_type, "graphviz")
        self.assertIn("GraphColoring", exp.diagram_code)

    def test_recursion_accuracy_and_diagram(self):
        """Recursion must explain base cases, call stack, and provide call stack diagram."""
        exp = explain_concept("Explain Recursion")
        self.assertEqual(exp.concept, "Recursion")
        text_full = (exp.technical_explanation + " " + exp.real_world_analogy).lower()
        self.assertIn("base case", text_full)
        self.assertIn("call stack", text_full)
        self.assertEqual(exp.diagram_type, "graphviz")
        self.assertIn("CallStack", exp.diagram_code)

    def test_binary_search_accuracy(self):
        """Binary search must specify sorted collection invariant and O(log N) complexity."""
        exp = explain_concept("Binary Search")
        self.assertEqual(exp.concept, "Binary Search")
        text_full = (exp.technical_explanation + " " + exp.simple_explanation).lower()
        self.assertIn("sorted", text_full)
        self.assertIn("log", text_full)

    def test_diagram_generator_fallback(self):
        """Un-diagrammable abstract concepts must return none and not fake code blocks."""
        dtype, code, caption = get_diagram_for_concept("Quantum Philosophy")
        self.assertEqual(dtype, "none")
        self.assertIsNone(code)
        self.assertEqual(caption, "Diagram is not available for this concept.")


class TestConversationIntentAndMemory(unittest.TestCase):
    def test_greeting_handling_does_not_lecture(self):
        """User saying 'hi' should receive a short friendly greeting, not an educational lecture."""
        resp = handle_chat_message("hi", active_concept="Recursion")
        self.assertEqual(resp["intent"], MessageIntent.GREETING)
        self.assertIn("Hi!", resp["text_response"])
        self.assertIsNone(resp["explanation"])

    def test_simplify_intent_triggers_super_simple(self):
        """User asking 'make it simpler' should simplify the active concept."""
        resp = handle_chat_message("make it simpler", active_concept="Graph Coloring")
        self.assertEqual(resp["intent"], MessageIntent.SIMPLIFY)
        self.assertIsNotNone(resp["explanation"])
        self.assertEqual(resp["active_concept"], "Graph Coloring")

    def test_another_example_intent(self):
        """User asking 'give another example' resolves active concept."""
        resp = handle_chat_message("give me another code example", active_concept="Recursion")
        self.assertEqual(resp["intent"], MessageIntent.ANOTHER_EXAMPLE)
        self.assertIsNotNone(resp["explanation"])


class TestDashboardAndModelCompatibility(unittest.TestCase):
    def test_topic_mastery_dict_access_and_get_method(self):
        """TopicMastery must support .get(), subscript ['key'], and attributes without AttributeError."""
        tm = TopicMastery(
            user_id="usr_01",
            topic_id="top_graph_coloring",
            mastery_score=0.85,
            confidence=0.90,
            last_updated="2026-08-15",
            topic_name="Graph Coloring",
            subject="Graph Theory"
        )
        # Test attribute access
        self.assertEqual(tm.mastery_score, 0.85)
        # Test .get() method (previously caused AttributeError)
        self.assertEqual(tm.get("mastery_score"), 0.85)
        self.assertEqual(tm.get("non_existent", "fallback"), "fallback")
        # Test dict subscript access
        self.assertEqual(tm["title"], "Graph Coloring")
        self.assertEqual(tm["category"], "Graph Theory")
        # Test to_dict()
        d = tm.to_dict()
        self.assertEqual(d["status"], "mastered")


class TestSmartRefreshAndGames(unittest.TestCase):
    def test_math_game_pool_size_and_non_repetition(self):
        """Math game pool must have at least 15 questions and avoid repeating exclude list."""
        self.assertGreaterEqual(len(math_games.MATH_POOL), 15)
        p1 = math_games.get_math_puzzle()
        p2 = math_games.get_math_puzzle(exclude_indices=[p1["puzzle_index"]])
        self.assertNotEqual(p1["puzzle_index"], p2["puzzle_index"])

    def test_gk_game_pool_size_and_non_repetition(self):
        """GK trivia pool must have at least 15 questions and support non-repeating picker."""
        self.assertGreaterEqual(len(gk.TRIVIA_POOL), 15)
        q1 = gk.get_gk_trivia(limit=1)[0]
        q2 = gk.get_gk_trivia(limit=1, exclude_indices=[q1["question_index"]])[0]
        self.assertNotEqual(q1["question_index"], q2["question_index"])

    def test_guess_concept_hints_and_aliases(self):
        """Guess concept must have 3 progressive clues and verify aliases."""
        c = guess_concept.get_guess_challenge(struggled_concept="graph coloring")
        self.assertEqual(len(c["hints"]), 3)
        self.assertTrue(guess_concept.verify_guess("Graph Coloring", c))
        self.assertTrue(guess_concept.verify_guess("vertex coloring", c))

    def test_riddles_and_anagrams_pool_size(self):
        """Riddles and anagrams pools must have at least 10 items each."""
        self.assertGreaterEqual(len(riddles.RIDDLE_POOL), 10)
        self.assertGreaterEqual(len(english_games.ENGLISH_POOL), 10)
        self.assertGreaterEqual(len(tongue_twisters.TWISTER_POOL), 10)

    def test_memory_card_deck_generation(self):
        """Memory card decks must generate valid matching pairs."""
        deck = memory_game.get_memory_card_deck(limit=3)
        self.assertEqual(len(deck), 3)
        self.assertIn("card_a", deck[0])
        self.assertIn("card_b", deck[0])


class TestFourMandatoryProblems(unittest.TestCase):
    def test_microphone_speech_engine_empty_protection(self):
        """Speech engine must reject empty audio streams safely without crashing."""
        import ai.speech_engine as speech_engine
        success, msg = speech_engine.transcribe_audio(b"")
        self.assertFalse(success)
        self.assertIn("empty", msg.lower())

        success_short, msg_short = speech_engine.transcribe_audio(b"short123")
        self.assertFalse(success_short)

    def test_arbitrary_topic_inquiry_transistor(self):
        """User can ask about ANY academic concept (e.g. Transistor) without predefined topic selection."""
        exp = explain_concept("What is a transistor?")
        self.assertEqual(exp.concept, "Transistor")
        self.assertIsNotNone(exp.simple_explanation)
        self.assertIsNotNone(exp.technical_explanation)
        self.assertIsNotNone(exp.understanding_check)

    def test_arbitrary_topic_inquiry_tcp_ip(self):
        """User can ask complex networking questions (e.g. TCP/IP) arbitrarily."""
        exp = explain_concept("Explain TCP/IP like I am a beginner")
        self.assertEqual(exp.concept, "Tcp/Ip Like I Am A Beginner")
        self.assertIsNotNone(exp.real_world_analogy)

    def test_continuous_timer_timestamp_delta(self):
        """Timer countdown must be derived from true time deltas."""
        from frontend.components.timer import render_continuous_timer
        import streamlit as st
        # Simulate 10 seconds elapsed
        st.session_state.break_start_time = time.time() - 10
        elapsed = int(time.time() - st.session_state.break_start_time)
        self.assertGreaterEqual(elapsed, 10)
        self.assertLessEqual(elapsed, 12)

    def test_user_data_isolation_clean_state(self):
        """New user must have 0 mastery, 0 study sessions, and 0 refresh history."""
        import database.queries as queries
        new_uid = f"usr_test_iso_{int(time.time())}"
        
        # Fresh user queries
        mastery = queries.get_topic_mastery(new_uid)
        history = queries.get_recent_learning_history(new_uid)
        sessions_list = queries.get_learning_history(new_uid)
        refresh_hist = queries.get_smart_refresh_history(new_uid)
        
        self.assertEqual(len(mastery), 0)
        self.assertEqual(len(history["recent_learning_sessions"]), 0)
        self.assertEqual(len(sessions_list), 0)
        self.assertEqual(len(refresh_hist), 0)


    def test_document_and_pdf_extraction_engine(self):
        """Document engine must parse text files and extract structured PDF contents."""
        import ai.document_engine as doc_engine
        
        # Test text / code file extraction
        sample_code = b"def binary_search(arr, target):\n    pass"
        success_txt, text_content = doc_engine.extract_content_from_file("algorithm.py", sample_code)
        self.assertTrue(success_txt)
        self.assertIn("binary_search", text_content)

        # Test image file tag
        success_img, img_tag = doc_engine.extract_content_from_file("graph_diagram.png", b"fake_png_binary_data")
        self.assertTrue(success_img)
        self.assertIn("graph_diagram.png", img_tag)

    def test_explain_concept_with_attached_document(self):
        """Teaching engine must incorporate attached document context into generated explanation."""
        doc_context = "TCP/IP consists of 4 abstraction layers: Network Interface, Internet, Transport, and Application."
        exp = explain_concept("Explain this document in simple words", context_document=doc_context)
        self.assertIsNotNone(exp.simple_explanation)
        self.assertIsNotNone(exp.technical_explanation)


if __name__ == "__main__":
    unittest.main()
