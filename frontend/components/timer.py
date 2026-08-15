"""
Smart Refresh 5-Minute Timer Component
Owner: Member 2 (UI/UX) & Member 4 (AI/ML + Smart Refresh)

Guarantees breaks are strictly capped at 5 minutes (300 seconds) using real clock timestamps.
"""

import streamlit as st
import time


def render_refresh_timer(max_seconds: int = 300) -> bool:
    """
    Displays a real-time countdown timer based on actual clock timestamps.
    Returns True if the 5-minute cap has expired.
    """
    if "break_start_time" not in st.session_state:
        st.session_state.break_start_time = time.time()
        
    elapsed = int(time.time() - st.session_state.break_start_time)
    remaining = max(0, max_seconds - elapsed)
    
    progress = max(0.0, min(1.0, remaining / max_seconds))
    mins, secs = divmod(remaining, 60)
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        if remaining < 60:
            st.error(f"⏱️ **Time Remaining: {mins:02d}:{secs:02d}** — Wrapping up your 5-minute break!")
        else:
            st.info(f"⏱️ **Smart Refresh Countdown: {mins:02d}:{secs:02d}** (5-min cap)")
    with col_t2:
        # Quick skip option for demo/testing convenience
        if st.button("⏭️ Complete Break", key="btn_skip_timer"):
            st.session_state.break_start_time = time.time() - max_seconds - 1
            return True

    st.progress(progress)
    
    if remaining <= 0:
        return True
        
    return False
