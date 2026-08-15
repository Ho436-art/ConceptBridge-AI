"""
Learning Interface Page - Conversational AI Learning Hub
Owner: Member 2 (UI/UX) & Technical Lead

Features:
- Pure conversational AI chat interface (NO forced dropdowns).
- Natural concept inquiry, multimodal input (image & audio upload), follow-up dialogues.
- Multi-tier concept cards (Analogy -> Simple -> Technical -> Practical -> Real Graphviz Diagram).
- Interactive understanding-check questions & feedback strategy pivots.
"""

import streamlit as st
import time
import ai.conversation_engine as conversation_engine
import ai.teaching_engine as teaching_engine
import ai.feedback_handler as feedback_handler
import ai.learner_profile as learner_profile_manager
import database.queries as queries
from frontend.components.concept_card import render_concept_card
from frontend.components.feedback_buttons import render_feedback_buttons


def show():
    # Ensure user is logged in
    user_id = st.session_state.get("current_user_id")
    if not user_id:
        st.warning("🔒 Please log in or sign up first.")
        return

    st.markdown("<h2>💬 AI Concept Learning Hub</h2>", unsafe_allow_html=True)
    st.caption("Ask any academic or technical concept. Learn through real-world analogies, deep dives, real diagrams, and interactive checks.")

    # Initialize chat session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "active_concept" not in st.session_state:
        st.session_state.active_concept = None
    if "current_explanation" not in st.session_state:
        st.session_state.current_explanation = None
    if "quiz_answered" not in st.session_state:
        st.session_state.quiz_answered = False

    # Check if a recommended topic was clicked from Dashboard
    if "load_recommended_topic" in st.session_state and st.session_state.load_recommended_topic:
        rec_topic = st.session_state.load_recommended_topic
        del st.session_state.load_recommended_topic
        _process_new_user_prompt(f"Explain {rec_topic}", user_id)
        st.rerun()

    # Top Multimodal & Quick Prompt Toolbar
    with st.expander("📎 Multimodal Input (Image / Audio Upload)", expanded=False):
        col_img, col_aud = st.columns(2)
        with col_img:
            uploaded_image = st.file_uploader(
                "📸 Upload homework diagram or math question image:",
                type=["png", "jpg", "jpeg", "webp"],
                key="chat_image_upload"
            )
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded concept question", width=300)
                if st.button("🔍 Analyze Image Question", key="btn_img_analyze"):
                    _process_new_user_prompt(f"Explain the concept shown in this diagram/image ({uploaded_image.name})", user_id)
                    st.rerun()
                    
        with col_aud:
            uploaded_audio = st.file_uploader(
                "🎙️ Voice question / audio recording:",
                type=["wav", "mp3", "m4a", "ogg"],
                key="chat_audio_upload"
            )
            if uploaded_audio:
                st.audio(uploaded_audio)
                if st.button("🎤 Transcribe & Ask Voice Query", key="btn_aud_ask"):
                    _process_new_user_prompt("Explain the recorded voice query concept", user_id)
                    st.rerun()

    # Quick Suggestion Pills
    st.markdown("<div style='margin-bottom: 12px;'>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("💡 Explain Graph Coloring", key="pill_graph"):
            _process_new_user_prompt("Explain Graph Coloring", user_id)
            st.rerun()
    with col_p2:
        if st.button("💡 Explain Recursion", key="pill_rec"):
            _process_new_user_prompt("Explain Recursion", user_id)
            st.rerun()
    with col_p3:
        if st.button("💡 Database Indexing", key="pill_db"):
            _process_new_user_prompt("Explain Database Indexing", user_id)
            st.rerun()
    with col_p4:
        if st.button("💡 What is an API?", key="pill_api"):
            _process_new_user_prompt("What is an API?", user_id)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 1. RENDER EXISTING CHAT CONVERSATION
    if not st.session_state.messages:
        # Welcome message on fresh session
        with st.chat_message("assistant", avatar="🌉"):
            st.markdown(
                "**Hello! I'm ConceptBridge AI.** 🌉\n\n"
                "Type any technical or academic concept you're studying (e.g. *'Explain Graph Coloring'*, *'What is Recursion'*, or *'How does Binary Search work?'*).\n"
                "I will guide you from *'I don't understand'* to *'Oh, it's that easy!'* with analogies, plain English, technical deep dives, and visual diagrams."
            )
    else:
        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🌉"):
                st.markdown(msg["content"])
                
                # If message contains an explanation payload, render the structured concept card
                if msg.get("explanation"):
                    render_concept_card(msg["explanation"])
                    
                    # If this is the latest explanation, render check question and feedback buttons
                    if idx == len(st.session_state.messages) - 1:
                        _render_interactive_check_and_feedback(msg["explanation"], user_id)

    # 2. CHAT INPUT AT BOTTOM
    prompt = st.chat_input("Ask any concept or follow-up question (e.g. 'Explain Graph Coloring', 'Make it simpler')...")
    if prompt:
        _process_new_user_prompt(prompt, user_id)
        st.rerun()


def _process_new_user_prompt(prompt_text: str, user_id: str):
    """Processes incoming chat input through conversational intent routing."""
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    st.session_state.quiz_answered = False

    # Get learner profile from database
    db_profile = queries.get_db_learner_profile(user_id) or {}
    
    # Process through conversation engine
    response_payload = conversation_engine.handle_chat_message(
        user_message=prompt_text,
        active_concept=st.session_state.active_concept,
        learner_profile=db_profile,
        previous_explanation=st.session_state.current_explanation
    )

    text_resp = response_payload.get("text_response", "")
    explanation_data = response_payload.get("explanation")
    new_active_concept = response_payload.get("active_concept") or st.session_state.active_concept

    if new_active_concept:
        st.session_state.active_concept = new_active_concept
    if explanation_data:
        st.session_state.current_explanation = explanation_data
        
        # Log learning session in database
        try:
            queries.create_topic_if_not_exists(
                topic_id=f"top_{new_active_concept.lower().replace(' ', '_')[:20]}",
                title=new_active_concept,
                category="Computer Science"
            )
            queries.save_learning_session(
                user_id=user_id,
                topic_id=f"top_{new_active_concept.lower().replace(' ', '_')[:20]}",
                duration=120
            )
        except Exception:
            pass

    st.session_state.messages.append({
        "role": "assistant",
        "content": text_resp,
        "explanation": explanation_data
    })


def _render_interactive_check_and_feedback(explanation_data: dict, user_id: str):
    """Renders understanding-check quiz and reaction feedback buttons."""
    check = explanation_data.get("understanding_check", {})
    concept = explanation_data.get("concept", "Concept")
    
    if check and isinstance(check, dict) and check.get("question"):
        st.markdown("---")
        st.markdown("#### 🎯 Quick Understanding Check")
        st.markdown(f"**{check.get('question')}**")
        
        options = check.get("options", [])
        if options:
            selected_choice = st.radio(
                "Choose the most accurate answer:",
                options,
                key=f"check_opt_{concept}_{len(st.session_state.messages)}"
            )
            
            if st.button("Submit Answer", key=f"btn_check_{concept}"):
                correct_ans = check.get("correct_answer", "")
                is_correct = selected_choice.strip() == correct_ans.strip() or (correct_ans in selected_choice)
                st.session_state.quiz_answered = True
                
                if is_correct:
                    st.success(f"🎉 **Correct!** {check.get('explanation', 'Great job grasping the concept!')}")
                    learner_profile_manager.update_mastery(
                        topic=concept,
                        performance={"is_correct": True, "difficulty": explanation_data.get("difficulty", "beginner")},
                        learner_profile={"user_id": user_id}
                    )
                else:
                    st.warning(f"🤔 **Not quite.** {check.get('explanation', 'Review the analogy or breakdown above.')}")
                    learner_profile_manager.update_mastery(
                        topic=concept,
                        performance={"is_correct": False, "difficulty": explanation_data.get("difficulty", "beginner")},
                        learner_profile={"user_id": user_id}
                    )

    # Reaction Feedback Buttons
    st.markdown("---")
    def on_feedback_received(fb_type: str):
        pivot_res = feedback_handler.process_feedback(
            feedback=fb_type,
            concept=concept,
            learner_profile={"user_id": user_id},
            previous_explanation=explanation_data
        )
        if pivot_res.get("strategy_changed") and pivot_res.get("alternative_explanation"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": pivot_res["encouraging_message"],
                "explanation": pivot_res["alternative_explanation"]
            })
            st.session_state.current_explanation = pivot_res["alternative_explanation"]
            st.rerun()
        else:
            st.toast(pivot_res.get("encouraging_message", "Feedback recorded!"), icon="👍")

    render_feedback_buttons(on_feedback=on_feedback_received)
