"""
Smart Refresh Engine Module
Owner: Member 4 (AI/ML + Smart Refresh)

Responsibilities:
- Fatigue/learning-state signal detection
- Smart Refresh session routing
- 5-minute hard limit enforcement (non-addictive return to study point)
- Cooldown guardrails
"""

import time
import random
from typing import Dict, Any, Optional

MAX_REFRESH_DURATION_SECONDS = 300  # Strict 5-minute cap
DEFAULT_COOLDOWN_MINUTES = 30.0

def is_cooldown_active(last_refresh_timestamp: Optional[float], cooldown_minutes: float = DEFAULT_COOLDOWN_MINUTES) -> bool:
    """
    Checks if the cooldown period is active since the last refresh session.
    """
    if last_refresh_timestamp is None:
        return False
    current_time = time.time()
    elapsed_seconds = current_time - last_refresh_timestamp
    return elapsed_seconds < (cooldown_minutes * 60.0)

def check_fatigue_signals(interaction_log: Dict[str, Any]) -> bool:
    """
    Examines study duration, consecutive errors, response latency, and other signals 
    to proactively suggest a break.
    """
    study_duration = interaction_log.get("study_duration_minutes", 0)
    consecutive_errors = interaction_log.get("consecutive_errors", 0)
    response_latency = interaction_log.get("response_latency_seconds", 0)
    repeated_hints = interaction_log.get("repeated_hints", 0)
    skipped_questions = interaction_log.get("skipped_questions", 0)
    performance_decline = interaction_log.get("performance_decline", False)
    user_reported_fatigue = interaction_log.get("user_reported_fatigue", False)
    
    # Heuristics for fatigue estimation
    if study_duration > 45:
        return True
    if consecutive_errors >= 3:
        return True
    if response_latency > 120:
        return True
    if repeated_hints >= 3:
        return True
    if skipped_questions >= 4:
        return True
    if performance_decline:
        return True
    if user_reported_fatigue:
        return True
        
    return False

def select_refresh_activity(learner_profile: Dict[str, Any],
                            recent_learning: Dict[str, Any],
                            fatigue_signals: Dict[str, Any]) -> str:
    """
    Determines an appropriate non-addictive micro-break activity based on the learner's state.
    """
    # 1. Exceeded exhaustion threshold or self-reported fatigue -> Relaxation or Friendly Chat
    if (fatigue_signals.get("user_reported_fatigue") or 
        learner_profile.get("user_reported_fatigue") or 
        fatigue_signals.get("exhaustion_level") == "high"):
        return random.choice(["relaxation", "friendly_chat"])
        
    # 2. Struggled with a concept/topic -> Guess the Concept (reinforce struggling concepts)
    if (recent_learning.get("struggled") or 
        len(learner_profile.get("struggled_concepts", [])) > 0):
        return "guess_concept"
        
    # 3. Long technical study session -> Memory Cards (for low-pressure term-definition pairing)
    if (recent_learning.get("is_technical") and 
        fatigue_signals.get("study_duration_minutes", 0) > 30):
        return "memory_game"
        
    # 4. General fun / default fallback -> GK, math, riddle, English games, tongue twisters
    activities = ["gk", "math_games", "riddles", "english_games", "tongue_twisters"]
    return random.choice(activities)

def start_refresh(learner_profile: Optional[Dict[str, Any]] = None,
                  recent_learning_context: Optional[Dict[str, Any]] = None,
                  last_refresh_timestamp: Optional[float] = None,
                  cooldown_minutes: float = DEFAULT_COOLDOWN_MINUTES) -> Dict[str, Any]:
    """
    Initializes a structured Smart Refresh session tailored to the learner's state.
    
    Args:
        learner_profile (dict, optional): Current learner profile state.
        recent_learning_context (dict, optional): Details of the current concept/topic studied.
        last_refresh_timestamp (float, optional): Timestamp of the last refresh completion.
        cooldown_minutes (float): Configurable cooldown length.
        
    Returns:
        dict: Refresh session payload including activity category, timer limit (300s),
              and resume checkpoint data.
    """
    profile = learner_profile or {}
    context = recent_learning_context or {}
    
    # Cooldown Guardrail
    if last_refresh_timestamp is not None and is_cooldown_active(last_refresh_timestamp, cooldown_minutes):
        cooldown_remaining = int((cooldown_minutes * 60.0) - (time.time() - last_refresh_timestamp))
        return {
            "session_status": "cooldown",
            "cooldown_remaining_seconds": max(0, cooldown_remaining),
            "max_duration_seconds": MAX_REFRESH_DURATION_SECONDS,
            "recommended_activity": None,
            "resume_checkpoint": context,
            "message": f"Cooldown active. Please wait {cooldown_remaining // 60}m {cooldown_remaining % 60}s before another refresh."
        }
        
    fatigue_signals = {
        "study_duration_minutes": context.get("study_duration_minutes", 0),
        "consecutive_errors": context.get("consecutive_errors", 0),
        "response_latency_seconds": context.get("response_latency_seconds", 0),
        "repeated_hints": context.get("repeated_hints", 0),
        "skipped_questions": context.get("skipped_questions", 0),
        "performance_decline": context.get("performance_decline", False),
        "user_reported_fatigue": profile.get("user_reported_fatigue", False) or context.get("user_reported_fatigue", False),
        "exhaustion_level": profile.get("exhaustion_level", "low")
    }
    
    selected_activity = select_refresh_activity(profile, context, fatigue_signals)
    suggest_break = check_fatigue_signals(fatigue_signals)
    
    return {
        "session_status": "ready",
        "max_duration_seconds": MAX_REFRESH_DURATION_SECONDS,
        "recommended_activity": selected_activity,
        "suggest_break": suggest_break,
        "resume_checkpoint": {
            "topic": context.get("topic"),
            "session_id": context.get("session_id"),
            "last_activity": context.get("last_activity"),
            "stopped_at": context.get("stopped_at")
        },
        "message": "Enjoy a healthy 5-minute recharge to restore focus!"
    }

def should_terminate_refresh(elapsed_seconds: float) -> bool:
    """
    Enforces the strict 5-minute (300 seconds) duration limit on the break.
    """
    return elapsed_seconds >= MAX_REFRESH_DURATION_SECONDS

