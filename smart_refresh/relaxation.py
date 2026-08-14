"""
Relaxation & Mindfulness Module
Owner: Member 4 (AI/ML + Smart Refresh)

Guided micro-relaxation: breathing, eye resting exercises, and posture resets.
"""

import random
from typing import Dict, Any, List, Optional

RELAXATION_ACTIVITIES = [
    {
        "title": "20-20-20 Eye Rest",
        "duration_minutes": 1,
        "steps": [
            "1. Look away from the screen.",
            "2. Focus on an object at least 20 feet away.",
            "3. Hold your gaze there for 20 seconds.",
            "4. Blink gently a few times.",
            "5. Take a deep breath and return focus."
        ]
    },
    {
        "title": "Box Breathing Reset",
        "duration_minutes": 2,
        "steps": [
            "1. Exhale completely through your mouth.",
            "2. Inhale quietly through your nose for 4 seconds.",
            "3. Hold your breath for 4 seconds.",
            "4. Exhale smoothly through your mouth for 4 seconds.",
            "5. Hold your lungs empty for 4 seconds.",
            "6. Repeat this cycle 3 times."
        ]
    },
    {
        "title": "Brief Physical Stretch",
        "duration_minutes": 1.5,
        "steps": [
            "1. Roll your shoulders backward 5 times slowly.",
            "2. Gently tilt your head to the left, holding for 10 seconds.",
            "3. Gently tilt your head to the right, holding for 10 seconds.",
            "4. Reach both arms overhead and stretch toward the ceiling.",
            "5. Release, take a slow breath, and relax."
        ]
    },
    {
        "title": "4-7-8 Breathing Technique",
        "duration_minutes": 2,
        "steps": [
            "1. Exhale completely with a whoosh sound.",
            "2. Close your mouth and inhale quietly through your nose for 4 seconds.",
            "3. Hold your breath for a count of 7 seconds.",
            "4. Exhale completely through your mouth for a count of 8 seconds.",
            "5. Repeat this breath cycle up to 4 times."
        ]
    }
]

def get_relaxation_activity(activity_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a guided relaxation micro-routine.
    
    If activity_type is specified, it returns the matching activity if found.
    Otherwise, it returns a random activity.
    """
    if activity_type:
        normalized = activity_type.lower()
        for act in RELAXATION_ACTIVITIES:
            if normalized in act["title"].lower():
                return act
                
    return random.choice(RELAXATION_ACTIVITIES)

