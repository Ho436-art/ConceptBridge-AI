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
    Provides light, encouraging replies based on simple keywords to keep the session light and finite.
    """
    msg_lower = user_message.lower()
    
    if "tired" in msg_lower or "exhausted" in msg_lower or "sleepy" in msg_lower:
        category = "tired"
    elif "stress" in msg_lower or "anxious" in msg_lower or "worry" in msg_lower or "hard" in msg_lower:
        category = "stressed"
    elif "bore" in msg_lower or "dull" in msg_lower:
        category = "bored"
    else:
        category = "default"
        
    response_template = RESPONSES[category]
    return response_template.format(user_name=user_name)

