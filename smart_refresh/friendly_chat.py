"""
Friendly Chat Module
Owner: Member 4 (AI/ML + Smart Refresh)

Lighthearted AI conversational break partner without heavy cognitive load.
"""

import random
from typing import Dict, Any, List

PROMPTS = [
    "Hey {user_name}! Great job studying so far. Need a joke, a fun fact, or just a quick chat before diving back in?",
    "Hello {user_name}, you've been working hard! Remember to blink and rest your eyes. What's on your mind?",
    "Hey there {user_name}! A study break is just what the brain ordered. How are you holding up?",
    "Hi {user_name}, taking a break is part of learning. Tell me, what's a non-technical interest of yours?"
]

RESPONSES = {
    "tired": "I hear you, {user_name}. Learning can take a lot of energy. Make sure to sit back, take a slow breath, and maybe grab some water. You are doing great!",
    "stressed": "Take a deep breath, {user_name}. You don't have to master everything in one go. Step by step, you're making real progress. How about we stretch?",
    "bored": "Boredom is just your brain asking for a change of pace. That's why we're on a break! Did you know that taking brief pauses improves focus by 20%?",
    "default": "That's interesting! Remember to keep it light so you can return to your studies with a fresh mind when the 5-minute timer finishes."
}

def get_friendly_chat_prompt(user_name: str = "Learner") -> str:
    """
    Returns the conversational framing for casual break chat.
    """
    selected_prompt = random.choice(PROMPTS)
    return selected_prompt.format(user_name=user_name)

def respond_to_user_message(user_message: str, user_name: str = "Learner") -> str:
    """
    Provides tailored, lighthearted break conversation via Groq LLM with contextual fallback.
    """
    clean_msg = user_message.strip()
    if not clean_msg:
        return f"I'm right here with you, {user_name}! Let's keep this 5-minute break relaxing. What's on your mind?"

    # 1. Try Groq AI generation for real contextual friendly chat
    try:
        from ai.llm_client import query_llm_text
        system_prompt = (
            f"You are the Friendly AI study-break companion for {user_name} in ConceptBridge AI. "
            "The student is currently taking a 5-minute relaxation break from studying. "
            "Reply warmly, humorously, and concisely (1-2 short friendly sentences). "
            "Do NOT lecture on technical concepts. Keep it fun, relaxing, and lighthearted."
        )
        ai_reply = query_llm_text(prompt=f"Student says: '{clean_msg}'", system_prompt=system_prompt)
        if ai_reply and len(ai_reply) > 5:
            return ai_reply
    except Exception:
        pass

    # 2. Contextual fallback if offline or during testing
    msg_lower = clean_msg.lower()
    if any(w in msg_lower for w in ["joke", "funny", "laugh"]):
        return f"Why do programmers prefer dark mode, {user_name}? Because light attracts bugs! 😄"
    elif any(w in msg_lower for w in ["doing", "up to", "what are you"]):
        return f"Just cheering you on, {user_name}! Relaxing your mind with a fresh mind makes your next study session twice as effective."
    elif any(w in msg_lower for w in ["tired", "exhausted", "sleepy"]):
        return f"I hear you, {user_name}. Close your eyes for 30 seconds and take a slow breath. You're doing awesome work today."
    elif any(w in msg_lower for w in ["stress", "anxious", "worry", "hard"]):
        return f"Take it one concept at a time, {user_name}. Learning is a marathon, not a sprint, and you are making steady progress! How about we stretch?"
    elif any(w in msg_lower for w in ["bore", "dull"]):
        return f"Boredom is just your brain asking for a change of pace, {user_name}! Did you know brief pauses improve your study focus by 20%?"
    elif any(w in msg_lower for w in ["okay", "ok", "did it", "done"]):
        return f"Awesome job, {user_name}! Feel free to stretch your shoulders or grab a sip of water with a fresh mind before our 5-minute timer finishes."
    elif any(w in msg_lower for w in ["hi", "hello", "hey"]):
        return f"Hey {user_name}! Great to chat with you during this break. How is your energy feeling right now?"

    return f"That's interesting, {user_name}! Remember to keep it light so you can return to your studies with a fresh mind when the 5-minute timer finishes."

