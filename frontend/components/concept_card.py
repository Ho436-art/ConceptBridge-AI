"""
Concept Card Component
Owner: Member 2 (UI/UX)

Renders modular explanation blocks (Analogy, Beginner, Technical, Example, Diagram).
"""

import streamlit as st
from typing import Dict, Any

def render_concept_card(explanation_data: Dict[str, Any]):
    """
    Renders structured multi-tier concept explanation in Streamlit.
    """
    st.subheader(f"💡 {explanation_data.get('concept', 'Concept')}")
    
    with st.expander("🌉 Real-World Analogy (Start Here!)", expanded=True):
        st.write(explanation_data.get("analogy", "No analogy provided."))
        
    with st.expander("🌱 Simple / Beginner Explanation", expanded=True):
        st.write(explanation_data.get("beginner_explanation", "No beginner explanation."))
        
    with st.expander("⚙️ Technical Deep-Dive", expanded=False):
        st.write(explanation_data.get("technical_explanation", "No technical explanation."))
        
    with st.expander("💻 Practical / Code Example", expanded=False):
        st.write(explanation_data.get("practical_example", "No code example."))
