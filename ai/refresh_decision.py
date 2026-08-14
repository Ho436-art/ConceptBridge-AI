"""
Smart Refresh Decision Engine
Owner: Member 1 (Team Lead / AI & ML)

Responsibilities:
- Cognitive load and fatigue signal evaluation (study duration, error streaks, response latency).
- Non-intrusive break recommendations (never forcibly interrupting the student).
- Configurable cooldown enforcement (default: 30 minutes) to prevent gaming/avoidance behavior.
- Support for explicit manual break requests ("I need a refresh").
"""

import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from models.schemas import RefreshDecision
from dotenv import load_dotenv

load_dotenv()

# Default 30-minute cooldown (configurable via environment variable)
DEFAULT_COOLDOWN_MINUTES = float(os.getenv("SMART_REFRESH_COOLDOWN_MINUTES", "30.0"))


def _check_cooldown(
    refresh_history: Optional[List[Dict[str, Any]]],
    cooldown_minutes: float = DEFAULT_COOLDOWN_MINUTES
) -> tuple[bool, float]:
    """
    Checks if a break was taken recently and computes remaining cooldown in minutes.
    
    Returns:
        (is_cooldown_active: bool, remaining_minutes: float)
    """
    if not refresh_history:
        return False, 0.0

    # Find the most recent refresh timestamp
    latest_ts = None
    for session in reversed(refresh_history):
        ts_str = session.get("created_at") or session.get("timestamp")
        if ts_str:
            try:
                latest_ts = datetime.fromisoformat(ts_str)
                break
            except Exception:
                pass

    if not latest_ts:
        return False, 0.0

    elapsed = datetime.now() - latest_ts
    elapsed_minutes = elapsed.total_seconds() / 60.0

    if elapsed_minutes < cooldown_minutes:
        remaining = round(cooldown_minutes - elapsed_minutes, 1)
        return True, remaining

    return False, 0.0


def calculate_fatigue_score(session_data: Dict[str, Any]) -> tuple[float, List[str]]:
    """
    Computes an estimated cognitive fatigue score (0.0 to 1.0) and associated reasons.
    """
    score = 0.0
    reasons = []

    # 1. Study Duration Factor (e.g. > 45 mins)
    duration_mins = float(session_data.get("study_duration_minutes", 0))
    if duration_mins >= 45:
        score += 0.35
        reasons.append(f"Continuous focus duration ({int(duration_mins)} mins)")
    elif duration_mins >= 25:
        score += 0.18

    # 2. Consecutive Error Streak
    consecutive_errors = int(session_data.get("consecutive_errors", 0))
    if consecutive_errors >= 3:
        score += 0.30
        reasons.append(f"Recent error streak ({consecutive_errors} consecutive misconceptions)")
    elif consecutive_errors == 2:
        score += 0.15

    # 3. Response Latency Trend
    latency_increasing = bool(session_data.get("latency_increasing", False))
    if latency_increasing:
        score += 0.15
        reasons.append("Response latency is trending higher")

    # 4. Hint Requests (Frustration signal)
    hint_count = int(session_data.get("hint_requests_count", 0))
    if hint_count >= 3:
        score += 0.15
        reasons.append(f"High hint usage ({hint_count} hints requested)")

    # 5. User Self-Reported Fatigue
    self_reported = bool(session_data.get("self_reported_fatigue", False))
    if self_reported:
        score += 0.40
        reasons.append("Learner self-reported tiredness")

    final_score = min(1.0, round(score, 2))
    return final_score, reasons


def should_offer_refresh(
    session_data: Dict[str, Any],
    refresh_history: Optional[List[Dict[str, Any]]] = None,
    cooldown_minutes: float = DEFAULT_COOLDOWN_MINUTES
) -> RefreshDecision:
    """
    Evaluates session telemetry to determine whether a 5-minute break should be recommended.
    
    Args:
        session_data: Telemetry dict containing study_duration_minutes, consecutive_errors, etc.
        refresh_history: Prior refresh logs.
        cooldown_minutes: Cooldown threshold in minutes.
        
    Returns:
        RefreshDecision: Structured decision with recommendation and cooldown status.
    """
    cooldown_active, remaining_mins = _check_cooldown(refresh_history, cooldown_minutes)
    fatigue_score, reasons = calculate_fatigue_score(session_data)

    # If cooldown is active, don't recommend a break unless severe self-reported fatigue
    if cooldown_active:
        return RefreshDecision(
            recommend_break=False,
            fatigue_score=fatigue_score,
            reasons=["Break cooldown is active."] + reasons,
            cooldown_active=True,
            cooldown_remaining_minutes=remaining_mins,
            suggested_activity=None,
            can_manual_request=False
        )

    # Recommend break if fatigue score meets threshold (>= 0.60)
    recommend = fatigue_score >= 0.60
    suggested_activity = None
    if recommend:
        if "tiredness" in str(reasons).lower() or session_data.get("study_duration_minutes", 0) > 40:
            suggested_activity = "relaxation"  # 20-20-20 eye rest & box breathing
        else:
            suggested_activity = "memory_game"  # Technical memory cards or quick riddle

    return RefreshDecision(
        recommend_break=recommend,
        fatigue_score=fatigue_score,
        reasons=reasons,
        cooldown_active=False,
        cooldown_remaining_minutes=0.0,
        suggested_activity=suggested_activity,
        can_manual_request=True
    )


def request_manual_refresh(
    session_data: Dict[str, Any],
    refresh_history: Optional[List[Dict[str, Any]]] = None,
    cooldown_minutes: float = DEFAULT_COOLDOWN_MINUTES,
    override_cooldown: bool = False
) -> RefreshDecision:
    """
    Handles explicit user manual break requests ("I need a refresh").
    """
    cooldown_active, remaining_mins = _check_cooldown(refresh_history, cooldown_minutes)

    if cooldown_active and not override_cooldown:
        return RefreshDecision(
            recommend_break=False,
            fatigue_score=0.5,
            reasons=[f"Cooldown active ({remaining_mins} minutes remaining). Take a quick stretch and continue studying!"],
            cooldown_active=True,
            cooldown_remaining_minutes=remaining_mins,
            suggested_activity=None,
            can_manual_request=False
        )

    return RefreshDecision(
        recommend_break=True,
        fatigue_score=1.0,
        reasons=["Manual request initiated by learner"],
        cooldown_active=False,
        cooldown_remaining_minutes=0.0,
        suggested_activity="friendly_chat",
        can_manual_request=True
    )
