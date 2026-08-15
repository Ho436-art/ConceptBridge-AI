"""
Learning Interface Page - Conversational AI Learning Hub
Owner: Member 2 (UI/UX) & Technical Lead

Features:
- Primary AI-chat Learning Hub where the user can ask to learn ANYTHING.
- Top / Center Dedicated Composer matching the exact user layout:
    [ Long Text Area: Ask anything you want to learn... ]
    [ 📎 Attach File | 🎤 Speak (Mic STT) | ➤ Send ]
- Floating bottom st.chat_input for quick follow-up inquiries.
- Speech-to-Text via Groq Whisper populates the input box for user review/edit before sending.
- PDF and document extraction with local pypdf parser.
- Multi-tier concept cards (Real-world analogy, simple breakdown, technical deep dive, practical example, code, Graphviz diagram, check quiz).
- Optional suggestion chips that never force topic selection.
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

    # Initialize chat session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "active_concept" not in st.session_state:
        st.session_state.active_concept = None
    if "current_explanation" not in st.session_state:
        st.session_state.current_explanation = None
    if "quiz_answered" not in st.session_state:
        st.session_state.quiz_answered = False
    if "transcribed_text_buffer" not in st.session_state:
        st.session_state.transcribed_text_buffer = ""
    if "attached_doc_context" not in st.session_state:
        st.session_state.attached_doc_context = None
    if "attached_doc_name" not in st.session_state:
        st.session_state.attached_doc_name = None

    # Check if a recommended topic was clicked from Dashboard
    if "load_recommended_topic" in st.session_state and st.session_state.load_recommended_topic:
        rec_topic = st.session_state.load_recommended_topic
        del st.session_state.load_recommended_topic
        _process_new_user_prompt(f"Explain {rec_topic}", user_id)
        st.rerun()

    # 1. HEADER (Clean, Centered, Student-Friendly)
    st.markdown(
        """
        <div style="text-align: center; margin-top: 10px; margin-bottom: 24px;">
            <h1 style="font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 6px;">
                🌉 ConceptBridge AI
            </h1>
            <p style="font-size: 1.15rem; color: #64748B; margin-top: 0;">
                What would you like to learn today?
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. PRIMARY MULTIMODAL COMPOSER CARD
    with st.container():
        st.markdown("<div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        # Long Text Area for Question
        user_typed_query = st.text_area(
            "Ask anything you want to learn...",
            value=st.session_state.transcribed_text_buffer,
            placeholder="Ask anything you want to learn (e.g. 'Explain recursion', 'What is a transistor?', 'Why is binary search faster?', 'Explain TCP/IP like I am a beginner')...",
            height=75,
            key="main_composer_textarea",
            label_visibility="collapsed"
        )
        
        # Action Toolbar Row: 📎 Attach File | 🎤 Speak (Mic) | ➤ Send
        col_attach, col_speak, col_send = st.columns([1.5, 1.5, 1])
        
        with col_attach:
            with st.popover("📎 Attach File (PDF / Image)"):
                uploaded_file = st.file_uploader(
                    "Upload document or image:",
                    type=["pdf", "png", "jpg", "jpeg", "webp", "txt", "py", "md"],
                    key="popover_file_uploader"
                )
                if uploaded_file:
                    success, extracted = document_engine.extract_content_from_file(uploaded_file.name, uploaded_file.getvalue())
                    if success:
                        st.session_state.attached_doc_context = extracted
                        st.session_state.attached_doc_name = uploaded_file.name
                        st.success(f"📎 Attached `{uploaded_file.name}`")
        
        with col_speak:
            with st.popover("🎤 Speak Question (Mic)"):
                st.caption("Click the red button, speak clearly, then click stop.")
                recorded_audio = st.audio_input("Record voice question:", key="composer_audio_recorder")
                if recorded_audio:
                    audio_bytes = recorded_audio.getvalue()
                    if audio_bytes and len(audio_bytes) > 500:
                        success, recognized_text = speech_engine.transcribe_audio(audio_bytes)
                        if success and recognized_text:
                            st.session_state.transcribed_text_buffer = recognized_text
                            st.success(f"Transcribed: *\"{recognized_text}\"*")
                            if st.button("Apply to Input Box", key="btn_apply_speech"):
                                st.rerun()
                        elif not success:
                            st.warning(f"⚠️ {recognized_text}")

        with col_send:
            if st.button("➤ Send", key="btn_composer_send", type="primary", use_container_width=True):
                query_to_process = user_typed_query.strip()
                doc_to_process = st.session_state.attached_doc_context
                
                if query_to_process or doc_to_process:
                    final_prompt = query_to_process if query_to_process else f"Explain the attached file: {st.session_state.attached_doc_name}"
                    st.session_state.transcribed_text_buffer = ""
                    st.session_state.attached_doc_context = None
                    st.session_state.attached_doc_name = None
                    _process_new_user_prompt(final_prompt, user_id, context_document=doc_to_process)
                    st.rerun()
                else:
                    st.warning("Please type a concept or record speech before sending.")

        if st.session_state.attached_doc_name:
            st.info(f"📎 **Attached:** `{st.session_state.attached_doc_name}` — Will be sent to the AI with your question.")

        st.markdown("</div>", unsafe_allow_html=True)

    # 3. OPTIONAL QUICK SUGGESTIONS (Purely optional examples, never mandatory)
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <span style="font-size: 0.88rem; color: #64748B; font-weight: 500;">Try asking:</span>
        </div>
        """,
        unsafe_allow_html=True
    )
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
        if st.button("💡 What is an API?", key="pill_api", use_container_width=True):
            _process_new_user_prompt("What is an API?", user_id)
            st.rerun()
    with col_p4:
        if st.button("💡 Explain Binary Search", key="pill_bsearch", use_container_width=True):
            _process_new_user_prompt("Why is binary search faster than linear search?", user_id)
            st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)

    # 4. RENDER EXISTING CHAT CONVERSATION
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🌉"):
            st.markdown(
                "**Hello! I'm ConceptBridge AI.** 🌉\n\n"
                "You can ask me to explain **any concept** you're studying — from computer science and mathematics to physics and engineering.\n"
                "I will bridge the gap from *'I don't understand'* to *'Oh, it's that easy!'* with intuitive analogies, plain English, technical mechanics, and interactive checks."
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

    # 5. FLOATING BOTTOM CHAT INPUT (For quick follow-ups)
    bottom_prompt = st.chat_input("Ask any follow-up question or new concept...")
    if bottom_prompt:
        context_doc = st.session_state.attached_doc_context
        st.session_state.attached_doc_context = None
        st.session_state.attached_doc_name = None
        _process_new_user_prompt(bottom_prompt.strip(), user_id, context_document=context_doc)
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
                category="General Learning"
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
            if msg and str(msg).strip():
                st.toast(str(msg).strip(), icon="👍")

    render_feedback_buttons(on_feedback=on_feedback_received)
