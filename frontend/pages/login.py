"""
Login & Onboarding View
Owner: Member 2 (UI/UX) - Enhanced for Seamless Hackathon Onboarding

Features:
- Demo account 1-click login or custom registration.
- Optional onboarding: Beginner, Intermediate, Advanced, Let AI Determine.
- 1-click skip onboarding option.
- Automatic routing to AI Chat Learning Hub upon authentication.
"""

import streamlit as st
import database.queries as queries


def show():
    st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h1>🌉 Welcome to <span class='gradient-text'>ConceptBridge AI</span></h1>", unsafe_allow_html=True)
    st.caption('From *"I don\'t understand"* to *"Oh, it\'s that easy!"*')
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Initialize session states
    if "current_user_id" not in st.session_state:
        st.session_state.current_user_id = None
    if "current_user_name" not in st.session_state:
        st.session_state.current_user_name = None
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = False
        
    # If a user is already logged in but onboarding is requested
    if st.session_state.current_user_id and st.session_state.onboarding_step:
        render_onboarding()
        return

    tab_login, tab_signup = st.tabs(["🔒 Log In", "📝 Sign Up"])
    
    with tab_login:
        st.markdown("<div class='glass-card' style='padding: 24px;'>", unsafe_allow_html=True)
        st.markdown("<h3>Sign in to your learning account</h3>", unsafe_allow_html=True)
        
        users = queries.get_all_users()
        
        if users:
            usernames = [u.get("username", u.get("name", "Student")) for u in users]
            selected_username = st.selectbox("Select existing profile", ["-- Choose a user --"] + usernames)
            st.markdown("<div style='text-align: center; margin: 10px 0; color: #888;'>— or enter credentials manually —</div>", unsafe_allow_html=True)
        else:
            selected_username = "-- Choose a user --"
            
        typed_username = st.text_input("Username or Email", placeholder="e.g. alex.mercer@conceptbridge.dev", key="login_user_input")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pwd")
        
        if st.button("Log In", type="primary", use_container_width=True):
            username_to_login = ""
            if typed_username.strip():
                username_to_login = typed_username.strip()
            elif selected_username != "-- Choose a user --":
                username_to_login = selected_username
                
            if not username_to_login:
                st.error("Please enter a username or select a profile.")
            else:
                matching_user = None
                for u in users:
                    u_name = u.get("username", u.get("name", ""))
                    u_email = u.get("email", "")
                    if username_to_login.lower() in [u_name.lower(), u_email.lower()]:
                        matching_user = u
                        break
                        
                if matching_user:
                    u_id = matching_user.get("user_id", str(matching_user))
                    u_name = matching_user.get("username", matching_user.get("name", username_to_login))
                    st.session_state.current_user_id = u_id
                    st.session_state.current_user_name = u_name
                    
                    profile = queries.get_db_learner_profile(u_id)
                    if not profile:
                        st.session_state.onboarding_step = True
                    else:
                        st.session_state.onboarding_step = False
                        st.session_state.navigation_selection = "📖 Learning Hub"
                    st.success(f"Welcome back, {u_name}!")
                    st.rerun()
                else:
                    # Auto-provision user for seamless hackathon testing
                    new_u = queries.create_user(username_to_login, f"{username_to_login.lower()}@demo.com")
                    st.session_state.current_user_id = getattr(new_u, "user_id", username_to_login)
                    st.session_state.current_user_name = username_to_login
                    st.session_state.onboarding_step = True
                    st.success(f"Created and logged in as {username_to_login}!")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_signup:
        st.markdown("<div class='glass-card' style='padding: 24px;'>", unsafe_allow_html=True)
        st.markdown("<h3>Create your companion account</h3>", unsafe_allow_html=True)
        
        new_username = st.text_input("Choose a username", placeholder="e.g. AdaLovelace", key="su_name")
        new_email = st.text_input("Email address (optional)", placeholder="ada@math.org", key="su_email")
        new_password = st.text_input("Password", type="password", placeholder="Create a password", key="su_pwd")
        
        if st.button("Create Account & Continue", type="primary", use_container_width=True):
            if not new_username.strip():
                st.error("Username is required.")
            else:
                user = queries.create_user(new_username.strip(), new_email.strip() or None)
                st.session_state.current_user_id = getattr(user, "user_id", user)
                st.session_state.current_user_name = new_username.strip()
                st.session_state.onboarding_step = True
                st.success("Account created successfully!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_onboarding():
    """
    Renders optional onboarding questionnaire with 1-click skip.
    """
    st.markdown("<div class='glass-card' style='padding: 28px;'>", unsafe_allow_html=True)
    st.markdown("<h2>🌱 Personalize Your Learning</h2>", unsafe_allow_html=True)
    st.caption("Tell us how you prefer to learn, or let our AI adapt dynamically as you study.")
    
    st.markdown("---")
    
    st.markdown("**What is your current technical knowledge level?**")
    level_choices = {
        "🌱 Beginner (Start from basics & analogies)": "beginner",
        "📘 Intermediate (Practical examples & code)": "intermediate",
        "🚀 Advanced (Technical deep-dives & architecture)": "advanced",
        "🤖 Let AI Determine (Calibrate dynamically based on my questions)": "let_ai_determine"
    }
    selected_label = st.radio(
        "Level selection", 
        list(level_choices.keys()), 
        index=3,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_submit, col_skip = st.columns(2)
    
    with col_submit:
        if st.button("Save & Start Learning", type="primary", use_container_width=True):
            level = level_choices[selected_label]
            queries.update_db_learner_profile(
                st.session_state.current_user_id,
                level,
                "analogy_first"
            )
            st.session_state.onboarding_step = False
            st.session_state.navigation_selection = "📖 Learning Hub"
            st.success("Preferences saved! Ready to learn.")
            st.rerun()
            
    with col_skip:
        if st.button("Skip — Let AI adapt dynamically", use_container_width=True):
            queries.update_db_learner_profile(
                st.session_state.current_user_id,
                "beginner",
                "analogy_first"
            )
            st.session_state.onboarding_step = False
            st.session_state.navigation_selection = "📖 Learning Hub"
            st.info("Onboarding skipped. AI will calibrate automatically.")
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
