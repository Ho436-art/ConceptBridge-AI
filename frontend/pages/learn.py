"""
Learning Interface Page - Conversational AI Learning Hub
Owner: Member 2 (UI/UX) & Technical Lead

Features:
- Primary Free-Form Chat Composer (accepts ANY academic or technical concept).
- Multimodal controls inside the same composer:
  * 📎 File Attachment: PDFs, Images, Code, Text documents.
  * 🎤 In-Browser Microphone: Live speech-to-text transcription into the editable text area.
  * ➤ Send: Dispatches query and attached document context to the AI Teaching Engine.
- Multi-tier concept cards (Analogy -> Simple -> Technical -> Practical -> Real Graphviz Diagram).
- Interactive understanding-check questions & feedback strategy pivots.
- Optional quick-example suggestion chips.
"""

import streamlit as st
import time
import ai.conversation_engine as conversation_engine
import ai.teaching_engine as teaching_engine
import ai.feedback_handler as feedback_handler
import ai.learner_profile as learner_profile_manager
import ai.speech_engine as speech_engine
import ai.document_engine as document_engine
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
    st.caption("Ask any academic or technical concept. Learn through real-world analogies, plain English, technical deep dives, real diagrams, and interactive checks.")

    # Initialize chat session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "active_concept" not in st.session_state:
        st.session_state.active_concept = None
    if "current_explanation" not in st.session_state:
        st.session_state.current_explanation = None
    if "quiz_answered" not in st.session_state:
        st.session_state.quiz_answered = False
    if "composer_text" not in st.session_state:
        st.session_state.composer_text = ""

    # Check if a recommended topic was clicked from Dashboard
    if "load_recommended_topic" in st.session_state and st.session_state.load_recommended_topic:
        rec_topic = st.session_state.load_recommended_topic
        del st.session_state.load_recommended_topic
        _process_new_user_prompt(f"Explain {rec_topic}", user_id)
        st.rerun()

    # 1. OPTIONAL QUICK SUGGESTION CHIPS (Purely optional examples)
    st.caption("💡 Quick Example Suggestions (Click any or type your own question in the composer):")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("💡 Explain Recursion", key="pill_rec", use_container_width=True):
            _process_new_user_prompt("Explain recursion in very simple words", user_id)
            st.rerun()
    with col_p2:
        if st.button("💡 What is a Transistor?", key="pill_transistor", use_container_width=True):
            _process_new_user_prompt("What is a transistor?", user_id)
            st.rerun()
    with col_p3:
        if st.button("💡 Graph Coloring", key="pill_graph", use_container_width=True):
            _process_new_user_prompt("Explain Graph Coloring", user_id)
            st.rerun()
    with col_p4:
        if st.button("💡 Explain TCP/IP", key="pill_tcp", use_container_width=True):
            _process_new_user_prompt("Explain TCP/IP like I am a beginner", user_id)
            st.rerun()

    st.markdown("---")

    # 2. RENDER EXISTING CHAT CONVERSATION
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🌉"):
            st.markdown(
                "**Hello! I'm ConceptBridge AI.** 🌉\n\n"
                "Type any technical or academic concept you want to learn (e.g. *'Explain recursion'*, *'What is a transistor?'*, *'Why does binary search require sorted data?'*, or upload a PDF/diagram).\n"
                "I will bridge the gap from *'I don't understand'* to *'Oh, it's that easy!'* with analogies, plain English, technical deep dives, and real visual diagrams."
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

    # 3. UNIFIED MULTIMODAL CHAT COMPOSER
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ✍️ Ask ConceptBridge")
    
    with st.container():
        # Attachment & Microphone Controls Row
        col_file, col_mic = st.columns([1, 1])
        
        with col_file:
            uploaded_file = st.file_uploader(
                "📎 Attach File (PDF, Image, Notes):",
                type=["pdf", "png", "jpg", "jpeg", "webp", "txt", "py", "md"],
                key="chat_composer_file"
            )
        
        with col_mic:
            st.markdown("<p style='font-size: 0.85rem; color: #aaa; margin: 0 0 4px 0;'>🎤 Speak Question (Microphone):</p>", unsafe_allow_html=True)
            recorded_audio = st.audio_input("Record voice question:", key="chat_composer_mic", label_visibility="collapsed")
            if recorded_audio:
                audio_bytes = recorded_audio.getvalue()
                if audio_bytes and len(audio_bytes) > 500:
                    success, recognized_text = speech_engine.transcribe_audio(audio_bytes)
                    if success and recognized_text:
                        st.session_state.composer_text = recognized_text
                        st.success(f"🎙️ **Transcribed:** *\"{recognized_text}\"*")
                    elif not success:
                        st.warning(f"⚠️ {recognized_text}")

        # Extract file context if attached
        file_context = None
        if uploaded_file:
            success, extracted = document_engine.extract_content_from_file(uploaded_file.name, uploaded_file.getvalue())
            if success:
                file_context = extracted
                st.info(f"📎 **Attached:** `{uploaded_file.name}` ({len(uploaded_file.getvalue())//1024} KB) — Will be sent to the AI with your question.")

        # Primary Long Free-Form Text Area Input
        user_query = st.text_area(
            "Ask any concept or question:",
            value=st.session_state.get("composer_text", ""),
            placeholder="Type any concept here (e.g. 'Explain recursion in simple words', 'What is a transistor?', 'Why does binary search require sorted data?')...",
            height=85,
            key="chat_composer_textarea"
        )

        col_send, col_clear, col_space = st.columns([2, 1, 4])
        with col_send:
            if st.button("➤ Send / Ask ConceptBridge", key="btn_send_prompt", type="primary", use_container_width=True):
                if user_query.strip() or file_context:
                    final_query = user_query.strip() if user_query.strip() else f"Explain the concept in attached file '{uploaded_file.name}'"
                    st.session_state.composer_text = ""
                    _process_new_user_prompt(final_query, user_id, context_document=file_context)
                    st.rerun()
                else:
                    st.warning("Please type a question or record speech before pressing Send.")

        with col_clear:
            if st.button("Clear", key="btn_clear_prompt", use_container_width=True):
                st.session_state.composer_text = ""
                st.rerun()


def _process_new_user_prompt(prompt_text: str, user_id: str, context_document: str = None):
    """Processes incoming chat input through conversational intent routing."""
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    st.session_state.quiz_answered = False

    # Get learner profile from database
    db_profile = queries.get_db_learner_profile(user_id) or {}
    
    # Process through conversation engine with optional document context
    response_payload = conversation_engine.handle_chat_message(
        user_message=prompt_text,
        active_concept=st.session_state.active_concept,
        learner_profile=db_profile,
        previous_explanation=st.session_state.current_explanation,
        context_document=context_document
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
            msg = pivot_res.get("encouraging_message") or "Feedback recorded!"
            st.toast(msg, icon="👍")

    render_feedback_buttons(on_feedback=on_feedback_received)
