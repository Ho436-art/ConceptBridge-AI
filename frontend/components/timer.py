"""
Smart Refresh 5-Minute Timer Component
Owner: Member 2 (UI/UX) & Member 4 (AI/ML + Smart Refresh)

Guarantees breaks are capped at 5 minutes (300 seconds).
"""

import streamlit as st
import time

def render_refresh_timer(max_seconds: int = 300) -> bool:
    """
    Displays a countdown timer and progress bar.
    Returns True if the timer has expired, otherwise False.
    """
    if "break_start_time" not in st.session_state:
        st.session_state.break_start_time = time.time()
        
    # Test accelerator option for verification ease
    fast_timer = st.sidebar.checkbox("⚡ Fast Break (for testing)", value=False, help="Runs the timer 20x faster for testing")
    speed_factor = 20.0 if fast_timer else 1.0
    
    elapsed = (time.time() - st.session_state.break_start_time) * speed_factor
    remaining = max(0, max_seconds - int(elapsed))
    
    progress = remaining / max_seconds
    mins, secs = divmod(remaining, 60)
    
    # Custom colored warning when time is low
    if remaining < 60:
        st.error(f"⏱️ **Time Remaining: {mins:02d}:{secs:02d}** - Wrap up your activity!")
    else:
        st.info(f"⏱️ **Time Remaining: {mins:02d}:{secs:02d}**")
        
    st.progress(progress)
    
    # Dev override button
    if st.sidebar.button("⏭️ Simulate Timer End", help="Instantly finish the break for testing"):
        st.session_state.break_start_time = time.time() - (max_seconds / speed_factor) - 1
        st.rerun()
        
    if remaining <= 0:
        return True
        
    return False
