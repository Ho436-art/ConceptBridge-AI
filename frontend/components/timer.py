"""
Smart Refresh 5-Minute Continuous Timer Component
Owner: Member 2 (UI/UX) & Member 4 (AI/ML + Smart Refresh)

Guarantees breaks are strictly capped at 5 minutes (300 seconds) using real clock timestamps
and auto-updates every second continuously without requiring user clicks or interaction.
"""

import streamlit as st
import time


@st.fragment(run_every=1)
def render_continuous_timer(max_seconds: int = 300) -> bool:
    """
    Renders an auto-updating countdown timer that ticks every 1 second automatically.
    Returns True when the time cap is reached.
    """
    if "break_start_time" not in st.session_state or not st.session_state.break_start_time:
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
            st.info(f"⏱️ **Smart Refresh Countdown: {mins:02d}:{secs:02d}** (Auto-updating 5-min cap)")
    with col_t2:
        if st.button("⏭️ Complete Break", key="btn_skip_timer"):
            st.session_state.break_start_time = time.time() - max_seconds - 1
            st.session_state.refresh_phase = "completed"
            st.rerun()

    st.progress(progress)
    
    if remaining <= 0:
        st.session_state.refresh_phase = "completed"
        return True
        
    return False


def render_refresh_timer(max_seconds: int = 300) -> bool:
    """Standard timer entry point."""
    return render_continuous_timer(max_seconds=max_seconds)
