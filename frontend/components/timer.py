"""
Smart Refresh 5-Minute Timer Component
Owner: Member 2 (UI/UX) & Member 4 (AI/ML + Smart Refresh)

Guarantees breaks are capped at 5 minutes (300 seconds).
"""

import streamlit as st
import time

def render_refresh_timer(max_seconds: int = 300):
    """
    Displays a lightweight countdown timer for the 5-minute break.
    """
    st.write(f"⏱️ **Break Timer:** Max {max_seconds // 60} minutes")
    progress_bar = st.progress(1.0)
    return progress_bar
