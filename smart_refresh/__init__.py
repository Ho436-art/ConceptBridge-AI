"""
Smart Refresh Subsystem for ConceptBridge AI.
Owner: Member 4 (AI/ML + Smart Refresh)

Provides lightweight, non-addictive 5-minute max micro-breaks:
- Technical memory-card games
- Guess-the-concept games with hints
- General knowledge trivia
- Fun mathematics
- English activities
- Tongue twisters
- Riddles
- Relaxation & breathing exercises
- Friendly AI conversation
"""

from .refresh_engine import start_refresh, check_fatigue_signals, MAX_REFRESH_DURATION_SECONDS

__all__ = [
    "start_refresh",
    "check_fatigue_signals",
    "MAX_REFRESH_DURATION_SECONDS"
]
