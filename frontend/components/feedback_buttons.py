"""
Feedback Buttons Component
Owner: Member 2 (UI/UX)

Renders comprehension buttons (e.g. "Crystal Clear!", "Still Confused", "Needs More Examples").
"""

import streamlit as st
from typing import Callable, Optional

def render_feedback_buttons(on_feedback: Optional[Callable[[str], None]] = None):
    """
    Renders quick feedback reactions for the learner.
    """
    st.write("How was this explanation?")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👍 Crystal Clear!"):
            if on_feedback:
                on_feedback("clear")
    with col2:
        if st.button("🤔 Still a Bit Fuzzy"):
            if on_feedback:
                on_feedback("fuzzy")
    with col3:
        if st.button("❓ Need Another Analogy"):
            if on_feedback:
                on_feedback("need_analogy")
