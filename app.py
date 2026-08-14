"""
ConceptBridge AI - Main Application Entry Point
Tagline: From "I don't understand" to "Oh, it's that easy!"

This is the primary entry point for the Streamlit web application.
It integrates frontend views, the AI teaching engine, database operations,
and the Smart Refresh subsystem following a strict separation of concerns.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from database.db import init_db
import database.queries as queries

# Load environment variables
load_dotenv()

# Initialize Database on Startup
init_db()

# Auto-seed database with development data on first run if empty
try:
    from database.seed import seed_development_data
    if not queries.get_all_topics():
        seed_development_data(reset_first=False)
except Exception as e:
    print(f"Error seeding database: {e}")

# Streamlit Page Configuration
st.set_page_config(
    page_title="ConceptBridge AI",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = None
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = False
if "navigation_selection" not in st.session_state:
    st.session_state.navigation_selection = "🔒 Log In / Sign Up"

# Inject Custom Style Assets
def load_css():
    css_path = "frontend/assets/style.css"
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css()

# Import Page Views
import frontend.pages.login as login_page
import frontend.pages.learn as learn_page
import frontend.pages.dashboard as dashboard_page
import frontend.pages.refresh as refresh_page

def main():
    # Sidebar navigation
    with st.sidebar:
        st.markdown("<h2>🌉 ConceptBridge</h2>", unsafe_allow_html=True)
        st.caption("From *\"I don't understand\"* to *\"Oh, it's that easy!\"*")
        st.markdown("---")
        
        # Define menu items based on session login state
        if not st.session_state.current_user_id:
            menu_options = ["🔒 Log In / Sign Up"]
            if st.session_state.navigation_selection not in menu_options:
                st.session_state.navigation_selection = "🔒 Log In / Sign Up"
        else:
            menu_options = [
                "📖 Learning Hub",
                "📊 Student Dashboard",
                "⚡ Smart Refresh (Break)",
                "⚙️ Settings"
            ]
            if st.session_state.navigation_selection not in menu_options:
                st.session_state.navigation_selection = "📖 Learning Hub"
                
        # Sidebar Navigation Dropdown / Radio list
        selection = st.radio(
            "Go to",
            menu_options,
            index=menu_options.index(st.session_state.navigation_selection) if st.session_state.navigation_selection in menu_options else 0
        )
        st.session_state.navigation_selection = selection
        
        # User details display in sidebar if logged in
        raw_uid = st.session_state.current_user_id
        user_id_str = getattr(raw_uid, "user_id", raw_uid) if raw_uid else None
        
        if user_id_str:
            st.markdown("---")
            profile = queries.get_db_learner_profile(user_id_str)
            if profile:
                st.write(f"👤 **Learner:** {st.session_state.current_user_name}")
                st.write(f"🌱 **Level:** {profile.get('estimated_level', 'beginner').capitalize()}")
                st.write(f"🎨 **Style:** {profile.get('preferred_learning_style', 'analogical').capitalize()}")
            
            # Fatigue / Break Recommendation Prompt
            st.markdown("---")
            st.markdown("**Fatigue Monitor**")
            # Proactive fatigue check: if they have studied 3+ times in history, prompt break
            history = queries.get_learning_history(user_id_str)
            if len(history) >= 3:
                st.warning("🧠 You've been working hard! Ready for a break?")
                col_br1, col_br2 = st.columns(2)
                with col_br1:
                    if st.button("Take Break", use_container_width=True):
                        st.session_state.navigation_selection = "⚡ Smart Refresh (Break)"
                        st.rerun()
                with col_br2:
                    st.button("Ignore", use_container_width=True)
            else:
                st.success("🟢 Energy Level: Focused")
            
            # Logout
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.current_user_id = None
                st.session_state.current_user_name = None
                st.session_state.onboarding_step = False
                st.session_state.navigation_selection = "🔒 Log In / Sign Up"
                st.rerun()
                
    # Page Routing Logic
    if st.session_state.navigation_selection == "🔒 Log In / Sign Up":
        if st.session_state.current_user_id and not st.session_state.onboarding_step:
            st.session_state.navigation_selection = "📖 Learning Hub"
            st.rerun()
        else:
            login_page.show()
            
    elif st.session_state.navigation_selection == "📖 Learning Hub":
        if st.session_state.onboarding_step:
            st.session_state.navigation_selection = "🔒 Log In / Sign Up"
            st.rerun()
        else:
            learn_page.show()
            
    elif st.session_state.navigation_selection == "📊 Student Dashboard":
        dashboard_page.show()
        
    elif st.session_state.navigation_selection == "⚡ Smart Refresh (Break)":
        refresh_page.show()
        
    elif st.session_state.navigation_selection == "⚙️ Settings":
        render_settings_page()

def render_settings_page():
    st.markdown("<h2>⚙️ Account Settings</h2>", unsafe_allow_html=True)
    st.write("Manage your learning styles, preferences, and account configuration.")
    
    user_id = st.session_state.get("current_user_id")
    profile = queries.get_db_learner_profile(user_id) or {}
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Update Onboarding Preferences")
    
    level_options = ["beginner", "intermediate", "advanced"]
    current_level = profile.get("estimated_level", "beginner")
    new_level = st.selectbox(
        "Estimated Knowledge Level", 
        level_options, 
        index=level_options.index(current_level) if current_level in level_options else 0
    )
    
    style_options = ["analogical", "visual", "practical", "technical"]
    current_style = profile.get("preferred_learning_style", "analogical")
    new_style = st.selectbox(
        "Preferred Learning Style", 
        style_options, 
        index=style_options.index(current_style) if current_style in style_options else 0
    )
    
    if st.button("Save Changes", type="primary", use_container_width=True):
        queries.update_db_learner_profile(user_id, new_level, new_style)
        st.success("Settings updated successfully!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
