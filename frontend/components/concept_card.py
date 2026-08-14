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
    Expects keys: concept, analogy, beginner_explanation, technical_explanation, practical_example, visual_explanation.
    """
    concept = explanation_data.get('concept', 'Concept')
    st.markdown(f"### 💡 Learning: <span class='gradient-text'>{concept}</span>", unsafe_allow_html=True)
    
    # Render with Streamlit tabs for high scannability and aesthetics
    tab_analogy, tab_beginner, tab_technical, tab_practical, tab_visual = st.tabs([
        "🌎 Real-World Analogy", 
        "💡 In Simple Words", 
        "🧠 Technical Explanation", 
        "🔧 Practical & Code", 
        "🖼️ Visual Diagram"
    ])
    
    with tab_analogy:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### 🌎 Real-World Analogy")
        st.write(explanation_data.get("analogy", "No analogy provided."))
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_beginner:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### 💡 In Simple Words")
        st.write(explanation_data.get("beginner_explanation", "No beginner explanation provided."))
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_technical:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### 🧠 Technical Deep-Dive")
        st.write(explanation_data.get("technical_explanation", "No technical explanation provided."))
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_practical:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔧 Practical & Code Example")
        practical = explanation_data.get("practical_example", "No code example provided.")
        if "```" in practical:
            st.write(practical)
        else:
            st.code(practical, language="python")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_visual:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### 🖼️ Visual / Diagram Block")
        visual = explanation_data.get("visual_explanation", "No diagram available.")
        if "+" in visual or "|" in visual or "-->" in visual:
            # Render ASCII diagram inside codeblock for proper monospace alignment
            st.code(visual, language="text")
        else:
            st.write(visual)
        st.markdown("</div>", unsafe_allow_html=True)
