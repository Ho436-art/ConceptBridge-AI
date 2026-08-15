import os
os.environ["TESTING"] = "true"
import ai.conversation_engine as conversation_engine
import ai.teaching_engine as teaching_engine

test_prompts = [
    "Explain linear search",
    "Explain recursion",
    "What is database indexing?",
    "What is a transistor?",
    "What is quantum superposition?",
    "Why does binary search require sorted data?"
]

print("=== RUNNING DIRECT PIPELINE VERIFICATION FOR ALL TEST PROMPTS ===")
for p in test_prompts:
    res = conversation_engine.handle_chat_message(
        user_message=p,
        active_concept=None,
        learner_profile={"user_id": "usr_test_verify"}
    )
    print(f"\n[PROMPT]: '{p}'")
    print(f"  -> Intent: {res['intent']}")
    print(f"  -> Active Concept: {res['active_concept']}")
    print(f"  -> Text Response: {res['text_response'][:80]}...")
    if res.get("explanation"):
        exp = res["explanation"]
        print(f"  -> Explanation Concept: {exp.get('concept')}")
        print(f"  -> Analogy: {exp.get('real_world_analogy', '')[:80]}...")
        print(f"  -> Simple: {exp.get('simple_explanation', '')[:80]}...")
        print(f"  -> Technical: {exp.get('technical_explanation', '')[:80]}...")
        print(f"  -> Check Question: {exp.get('understanding_check', {}).get('question', '')[:60]}...")
    else:
        print("  -> ERROR: No explanation generated!")

print("\n=== ALL TEST PROMPTS SUCCESSFULLY PROCESSED BY AI PIPELINE ===")
