"""
Feedback Buttons Component
Owner: Member 2 (UI/UX)

Renders comprehension feedback buttons and follow-up explanation options.
"""

import streamlit as st
from typing import Callable, Optional

def render_feedback_buttons(on_feedback: Optional[Callable[[str], None]] = None):
    """
    Renders reaction buttons for the explanation.
    If 'Still confused' is selected, triggers sub-options for follow-up style.
    """
    st.write("**How was that explanation?**")
    
    col1, col2, col3 = st.columns(3)
    
    # Store selected feedback type in st.session_state to toggle follow-up options
    if "feedback_selection" not in st.session_state:
        st.session_state.feedback_selection = None
        
    with col1:
        if st.button("🙂 Got it", use_container_width=True):
            st.session_state.feedback_selection = "got_it"
            if on_feedback:
                on_feedback("got_it")
                
    with col2:
        if st.button("😐 Almost", use_container_width=True):
            st.session_state.feedback_selection = "almost"
            if on_feedback:
                on_feedback("almost")
                
    with col3:
        if st.button("😕 Still confused", use_container_width=True):
            st.session_state.feedback_selection = "confused"
            # We don't trigger the callback immediately because the user needs to select how they want it resolved

    if st.session_state.feedback_selection == "confused":
        st.markdown("<div class='tip-banner' style='margin-top: 15px;'>", unsafe_allow_html=True)
        st.markdown("**What would help make this concept clearer?**")
        
        # Sub-options for resolving confusion
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            if st.button("🌎 Explain with another analogy", use_container_width=True):
                st.session_state.feedback_selection = None  # Reset
                if on_feedback:
                    on_feedback("need_another_analogy")
            if st.button("🧒 Make it simpler", use_container_width=True):
                st.session_state.feedback_selection = None
                if on_feedback:
                    on_feedback("make_simpler")
            if st.button("📊 Explain visually", use_container_width=True):
                st.session_state.feedback_selection = None
                if on_feedback:
                    on_feedback("explain_visually")
        with col_opt2:
            if st.button("💻 Show an example", use_container_width=True):
                st.session_state.feedback_selection = None
                if on_feedback:
                    on_feedback("show_example")
            if st.button("🎯 Give a practical example", use_container_width=True):
                st.session_state.feedback_selection = None
                if on_feedback:
                    on_feedback("practical_example")
            if st.button("❌ Close Options", use_container_width=True):
                st.session_state.feedback_selection = None
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)
