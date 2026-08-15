"""
Concept Card Component
Owner: Member 2 (UI/UX) - Enhanced for Real Diagram Rendering & Accuracy

Renders structured multi-tier explanation blocks (Analogy, Simple, Technical, Practical Code, Real Diagrams, and Understanding Checks).
"""

import streamlit as st
from typing import Dict, Any, Optional
from ai.diagram_generator import get_diagram_for_concept


def render_concept_card(explanation_data: Dict[str, Any]):
    """
    Renders structured multi-tier concept explanation in Streamlit.
    """
    concept = explanation_data.get("concept", "Concept")
    difficulty = explanation_data.get("difficulty", "beginner").upper()
    style_used = explanation_data.get("style_used", "analogy_first").replace("_", " ").title()

    st.markdown(
        f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
            <h3 style='margin: 0; color: #4D96FF;'>💡 Learning: {concept}</h3>
            <span class='onboarding-badge' style='background: rgba(77, 150, 255, 0.15); border: 1px solid rgba(77, 150, 255, 0.3); font-size: 0.8rem;'>
                Difficulty: {difficulty}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render with Streamlit tabs for scannability and modular depth
    tab_analogy, tab_beginner, tab_technical, tab_practical, tab_visual = st.tabs([
        "🌎 Real-World Analogy", 
        "💡 In Simple Words", 
        "🧠 Technical Explanation", 
        "🔧 Practical & Code", 
        "🖼️ Visual Diagram"
    ])
    
    with tab_analogy:
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.markdown("#### 🌎 Real-World Analogy (Start Here!)")
        st.write(explanation_data.get("real_world_analogy") or explanation_data.get("analogy", "No analogy provided."))
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_beginner:
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.markdown("#### 💡 In Simple Words")
        st.write(explanation_data.get("simple_explanation") or explanation_data.get("beginner_explanation", "No beginner explanation provided."))
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_technical:
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.markdown("#### 🧠 Technical Deep-Dive")
        st.write(explanation_data.get("technical_explanation", "No technical explanation provided."))
        
        # Key takeaways bullets
        takeaways = explanation_data.get("key_takeaways", [])
        if takeaways and isinstance(takeaways, list):
            st.markdown("<br><strong>Key Principles:</strong>", unsafe_allow_html=True)
            for point in takeaways:
                st.markdown(f"• {point}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_practical:
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.markdown("#### 🔧 Practical Application & Code")
        app_text = explanation_data.get("practical_application") or explanation_data.get("practical_example", "")
        if app_text:
            st.write(app_text)
            st.markdown("---")
            
        code_demo = explanation_data.get("example_code_or_visual", "")
        if code_demo:
            if "```" in code_demo:
                st.markdown(code_demo)
            elif "\n" in code_demo and ("def " in code_demo or "import " in code_demo or "SELECT " in code_demo):
                st.code(code_demo, language="python")
            else:
                st.write(code_demo)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_visual:
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.markdown("#### 🖼️ Visual Model")
        
        # Check diagram properties
        diag_type = explanation_data.get("diagram_type", "none")
        diag_code = explanation_data.get("diagram_code")
        diag_caption = explanation_data.get("diagram_caption", "")
        
        # If diagram was not attached in dict, query diagram generator dynamically
        if (not diag_code or diag_type == "none") and concept:
            diag_type, diag_code, diag_caption = get_diagram_for_concept(concept)

        if diag_type == "graphviz" and diag_code:
            try:
                st.graphviz_chart(diag_code)
                if diag_caption:
                    st.caption(f"📌 {diag_caption}")
            except Exception as e:
                st.info("Diagram is not available for this concept.")
        elif diag_type == "mermaid" and diag_code:
            st.markdown(f"```mermaid\n{diag_code}\n```")
            if diag_caption:
                st.caption(f"📌 {diag_caption}")
        else:
            st.info("Diagram is not available for this concept.")
            
        st.markdown("</div>", unsafe_allow_html=True)
