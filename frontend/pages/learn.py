"""
Learning Interface Page
Owner: Member 2 (UI/UX)
"""

import streamlit as st
import ai.teaching_engine as teaching_engine
import database.queries as queries
from frontend.components.concept_card import render_concept_card
from frontend.components.feedback_buttons import render_feedback_buttons

def show():
    # Ensure user is logged in
    user_id = st.session_state.get("current_user_id")
    if not user_id:
        st.warning("🔒 Please log in or sign up first.")
        return

    st.markdown("<h2>📖 Concept Learning Hub</h2>", unsafe_allow_html=True)
    st.write("Explore complex topics broken down into real-world analogies, simplified concepts, and interactive code examples.")
    
    # Check if a recommended topic was clicked in dashboard and load it
    recommended_topic = st.session_state.get("load_recommended_topic")
    
    # Get user profile
    profile = queries.get_db_learner_profile(user_id) or {
        "estimated_level": "beginner",
        "preferred_learning_style": "analogical"
    }
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("#### 🔍 What would you like to learn today?", unsafe_allow_html=True)
    
    # Dropdown with popular seeded topics
    db_topics = queries.get_all_topics()
    topic_titles = [t["title"] for t in db_topics]
    
    selected_topic_title = st.selectbox(
        "Choose a seeded topic...", 
        ["-- Select Topic --"] + topic_titles,
        index=topic_titles.index(recommended_topic) + 1 if recommended_topic in topic_titles else 0
    )
    
    # Clear the recommended topic redirect from dashboard
    if "load_recommended_topic" in st.session_state:
        del st.session_state.load_recommended_topic
        
    custom_concept = st.text_input(
        "Or type any custom concept (e.g. Recursion, Neural Networks, PCA):", 
        placeholder="Type a concept here..."
    )
    
    # Explanation trigger button
    btn_explain = st.button("🚀 Explain to Me!", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    concept_to_query = None
    if btn_explain:
        if custom_concept.strip():
            concept_to_query = custom_concept.strip()
        elif selected_topic_title != "-- Select Topic --":
            concept_to_query = selected_topic_title
            
        if not concept_to_query:
            st.error("Please select a topic or enter a custom concept.")
            
    # Process and fetch explanation
    if concept_to_query:
        with st.spinner(f"AI is preparing an explanation for '{concept_to_query}'..."):
            explanation_data = teaching_engine.explain_concept(concept_to_query, profile)
            
            # Map topic in DB
            topic_id = concept_to_query.lower().replace(" ", "_")
            category = "General"
            for t in db_topics:
                if t["title"].lower() == concept_to_query.lower():
                    topic_id = t["topic_id"]
                    category = t["category"]
                    break
            
            queries.create_topic_if_not_exists(topic_id, concept_to_query, category)
            
            # Save history log in database
            history_id = queries.save_learning_history(
                user_id=user_id,
                topic_id=topic_id,
                concept_query=concept_to_query,
                analogy=explanation_data.get("analogy", ""),
                level=explanation_data.get("knowledge_level_targeted", "beginner"),
                time_spent=45 # mock study time duration
            )
            
            # Save explanation and active topic state
            st.session_state.current_explanation = explanation_data
            st.session_state.current_topic_id = topic_id
            st.session_state.current_topic_title = concept_to_query
            st.session_state.current_history_id = history_id
            # Reset chat history for the new topic
            st.session_state.chat_history = []
            
    # Render active explanation
    if "current_explanation" in st.session_state and st.session_state.current_explanation:
        explanation = st.session_state.current_explanation
        topic_id = st.session_state.current_topic_id
        topic_title = st.session_state.current_topic_title
        history_id = st.session_state.current_history_id
        
        st.markdown("---")
        render_concept_card(explanation)
        
        # Feedback Buttons Callback
        def handle_feedback(feedback_type: str):
            rating_map = {
                "got_it": 5,
                "almost": 3,
                "confused": 2,
                "need_another_analogy": 2,
                "make_simpler": 2,
                "explain_visually": 2,
                "show_example": 2,
                "practical_example": 2
            }
            db_feedback_type = "still_confused"
            if feedback_type in ["got_it", "almost", "still_confused"]:
                db_feedback_type = feedback_type
                
            # Log in database feedback table using real database schema
            queries.save_feedback(
                user_id=user_id,
                topic_id=topic_id,
                feedback_type=db_feedback_type
            )
            
            # Update mastery delta based on feedback
            mastery_delta = 0.0
            feedback_msg = ""
            
            if feedback_type == "got_it":
                mastery_delta = 0.15
                feedback_msg = "🎉 Awesome! Your mastery score for this topic has increased!"
            elif feedback_type == "almost":
                mastery_delta = 0.05
                feedback_msg = "👍 Great progress! Practice makes perfect."
            elif feedback_type == "need_another_analogy":
                feedback_msg = "💡 Noted! The teaching engine will focus on secondary analogies next."
            elif feedback_type == "make_simpler":
                feedback_msg = "🧒 Got it! We will focus on simpler vocabulary terms."
            elif feedback_type == "explain_visually":
                feedback_msg = "📊 Visual aids and ASCII diagrams prioritized."
            elif feedback_type == "show_example":
                feedback_msg = "💻 Additional code segments will be curated."
            elif feedback_type == "practical_example":
                feedback_msg = "🎯 Applied real-world cases logged."
                
            queries.update_mastery(user_id, topic_id, mastery_delta)
            st.toast(feedback_msg, icon="💡")
            
        # Render feedback module
        render_feedback_buttons(handle_feedback)
        
        # Follow-up Chat Interface
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 💬 Ask Follow-up Questions")
        st.caption("Ask questions to clarify specific parts of the concept or request alternative explanations.")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        # Display chat messages
        for role, text in st.session_state.chat_history:
            with st.chat_message(role):
                st.write(text)
                
        # Chat input box
        if question := st.chat_input("Ask a follow-up (e.g., 'What is a base case?', 'What happens if we hit the recursion limit?')"):
            with st.chat_message("user"):
                st.write(question)
            st.session_state.chat_history.append(("user", question))
            
            with st.spinner("AI is thinking..."):
                response = teaching_engine.answer_follow_up(topic_title, question, profile)
                
            with st.chat_message("assistant"):
                st.write(response)
            st.session_state.chat_history.append(("assistant", response))
            st.rerun()
