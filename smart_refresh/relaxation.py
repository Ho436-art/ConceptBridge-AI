"""
Relaxation & Mindfulness Module
Owner: Member 4 (AI/ML + Smart Refresh)

Guided micro-relaxation: 4-7-8 breathing, eye resting exercises, and posture resets.
"""

from typing import Dict, Any, List

def get_relaxation_activity() -> Dict[str, Any]:
    """
    Returns a 2 to 3 minute guided relaxation micro-routine.
    """
    return {
        "title": "20-20-20 Eye Rest & Box Breathing",
        "duration_minutes": 2,
        "steps": [
            "1. Look away from the screen at an object 20 feet away for 20 seconds.",
            "2. Inhale deeply through your nose for 4 seconds.",
            "3. Hold your breath for 4 seconds.",
            "4. Exhale smoothly through your mouth for 4 seconds.",
            "5. Repeat 3 times, roll your shoulders, and relax."
        ]
    }
