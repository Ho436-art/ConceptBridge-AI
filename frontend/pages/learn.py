"""
Learning Interface Page - Conversational AI Learning Hub
Owner: Member 2 (UI/UX) & Technical Lead

Features:
- Primary Free-Form Chat Input (st.chat_input) that processes ANY academic/technical concept.
- Multimodal toolbar (PDF & Image file upload + in-browser live microphone speech-to-text).
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
    if "attached_doc_context" not in st.session_state:
        st.session_state.attached_doc_context = None
    if "attached_doc_name" not in st.session_state:
        st.session_state.attached_doc_name = None
    if "voice_transcript" not in st.session_state:
        st.session_state.voice_transcript = None

    # Check if a recommended topic was clicked from Dashboard
    if "load_recommended_topic" in st.session_state and st.session_state.load_recommended_topic:
        rec_topic = st.session_state.load_recommended_topic
        del st.session_state.load_recommended_topic
        _process_new_user_prompt(f"Explain {rec_topic}", user_id)
        st.rerun()

    # 1. OPTIONAL QUICK SUGGESTION CHIPS (Click any or type your own question below)
    st.caption("💡 Quick Example Suggestions (Click any or type your own question in the chat bar below):")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("💡 Explain Linear Search", key="pill_linear", use_container_width=True):
            _process_new_user_prompt("Explain linear search", user_id)
            st.rerun()
    with col_p2:
        if st.button("💡 Explain Recursion", key="pill_rec", use_container_width=True):
            _process_new_user_prompt("Explain recursion in very simple words", user_id)
            st.rerun()
    with col_p3:
        if st.button("💡 What is a Transistor?", key="pill_transistor", use_container_width=True):
            _process_new_user_prompt("What is a transistor?", user_id)
            st.rerun()
    with col_p4:
        if st.button("💡 What is DB Indexing?", key="pill_db", use_container_width=True):
            _process_new_user_prompt("What is database indexing?", user_id)
            st.rerun()

    # 2. MULTIMODAL TOOLBAR (Attach PDF/Image & Live Microphone Recording)
    with st.expander("📎 Attach Document / 🎤 Live Microphone Input", expanded=bool(st.session_state.attached_doc_name or st.session_state.voice_transcript)):
        col_file, col_mic = st.columns(2)
        
        with col_file:
            st.markdown("#### 📎 Attach File (PDF, Image, Notes)")
            uploaded_file = st.file_uploader(
                "Choose a PDF or image:",
                type=["pdf", "png", "jpg", "jpeg", "webp", "txt", "py", "md"],
                key="multimodal_file_uploader"
            )
            if uploaded_file:
                success, extracted = document_engine.extract_content_from_file(uploaded_file.name, uploaded_file.getvalue())
                if success:
                    st.session_state.attached_doc_context = extracted
                    st.session_state.attached_doc_name = uploaded_file.name
                    st.success(f"📎 Attached `{uploaded_file.name}` ({len(uploaded_file.getvalue())//1024} KB)")
                    if st.button("🔍 Explain Attached File Now", key="btn_explain_doc", type="primary"):
                        _process_new_user_prompt(
                            f"Explain the concept in this attached file ({uploaded_file.name})",
                            user_id,
                            context_document=extracted
                        )
                        st.session_state.attached_doc_context = None
                        st.session_state.attached_doc_name = None
                        st.rerun()

        with col_mic:
            st.markdown("#### 🎤 In-Browser Microphone")
            st.caption("Click record, speak your question, then click stop.")
            recorded_audio = st.audio_input("Record voice question:", key="multimodal_mic_input")
            if recorded_audio:
                audio_bytes = recorded_audio.getvalue()
                if audio_bytes and len(audio_bytes) > 500:
                    success, recognized_text = speech_engine.transcribe_audio(audio_bytes)
                    if success and recognized_text:
                        st.session_state.voice_transcript = recognized_text
                    elif not success:
                        st.warning(f"⚠️ {recognized_text}")

            if st.session_state.voice_transcript:
                st.markdown(f"**Recognized Speech:** *\"{st.session_state.voice_transcript}\"*")
                col_va, col_vc = st.columns([2, 1])
                with col_va:
                    if st.button("🚀 Ask Transcribed Question", key="btn_ask_voice", type="primary", use_container_width=True):
                        query_to_send = st.session_state.voice_transcript
                        st.session_state.voice_transcript = None
                        _process_new_user_prompt(query_to_send, user_id)
                        st.rerun()
                with col_vc:
                    if st.button("Clear Voice", key="btn_clear_voice_mic", use_container_width=True):
                        st.session_state.voice_transcript = None
                        st.rerun()

    if st.session_state.attached_doc_name:
        st.info(f"📎 **Attached to next message:** `{st.session_state.attached_doc_name}` — Type your question below to ask about it!")

    st.markdown("---")

    # 3. RENDER EXISTING CHAT CONVERSATION
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🌉"):
            st.markdown(
                "**Hello! I'm ConceptBridge AI.** 🌉\n\n"
                "Type any technical or academic concept you want to learn below (e.g. *'Explain linear search'*, *'Explain recursion'*, *'What is a transistor?'*, or *'What is database indexing?'*).\n"
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

    # 4. PRIMARY FREE-FORM CHAT INPUT COMPOSER (Floating Bottom Bar)
    user_prompt = st.chat_input(
        "Ask any concept or question (e.g. 'Explain linear search', 'Explain recursion', 'What is a transistor?')..."
    )
    
    if user_prompt:
        context_doc = st.session_state.attached_doc_context
        # Clear attached context after using
        st.session_state.attached_doc_context = None
        st.session_state.attached_doc_name = None
        
        _process_new_user_prompt(user_prompt.strip(), user_id, context_document=context_doc)
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
