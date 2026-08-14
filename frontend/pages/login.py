"""
Login & Onboarding View
Owner: Member 2 (UI/UX)
"""

import streamlit as st
import database.queries as queries

def show():
    st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h1>🌉 Welcome to <span class='gradient-text'>ConceptBridge AI</span></h1>", unsafe_allow_html=True)
    st.caption('From *"I don\'t understand"* to *"Oh, it\'s that easy!"*')
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Initialize session states if they don't exist
    if "current_user_id" not in st.session_state:
        st.session_state.current_user_id = None
    if "current_user_name" not in st.session_state:
        st.session_state.current_user_name = None
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = False
        
    # If a user is already logged in but onboarding is active
    if st.session_state.current_user_id and st.session_state.onboarding_step:
        render_onboarding()
        return

    # Tabs for login and signup
    tab_login, tab_signup = st.tabs(["🔒 Log In", "📝 Sign Up"])
    
    with tab_login:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Sign in to your learning account</h3>", unsafe_allow_html=True)
        
        users = queries.get_all_users()
        
        if users:
            usernames = [u["username"] for u in users]
            selected_username = st.selectbox("Select existing profile", ["-- Choose a user --"] + usernames)
            
            st.markdown("<div style='text-align: center; margin: 15px 0;'>or</div>", unsafe_allow_html=True)
        else:
            selected_username = "-- Choose a user --"
            st.info("No registered users found. Please sign up or enter a username below.")
            
        typed_username = st.text_input("Enter your username to login", placeholder="e.g. JohnDoe")
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
                # Find user or create if they typed a new one but clicked Login
                matching_user = next((u for u in users if u["username"].lower() == username_to_login.lower()), None)
                if matching_user:
                    st.session_state.current_user_id = matching_user["user_id"]
                    st.session_state.current_user_name = matching_user["username"]
                    # Fetch learner profile to see if style preference exists
                    profile = queries.get_db_learner_profile(matching_user["user_id"])
                    if profile and profile.get("preferred_learning_style") and profile.get("preferred_learning_style") != "analogical":
                        st.session_state.onboarding_step = False
                    else:
                        st.session_state.onboarding_step = True  # Show onboarding to configure style
                    st.success(f"Logged in successfully as {matching_user['username']}!")
                    st.rerun()
                else:
                    st.error("Username not found. Please Sign Up first.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_signup:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Create your companion account</h3>", unsafe_allow_html=True)
        
        new_username = st.text_input("Choose a username", placeholder="e.g. MarieCurie")
        new_email = st.text_input("Email address (optional)", placeholder="marie@science.edu")
        new_password = st.text_input("Password", type="password", placeholder="Create a strong password", key="signup_pwd")
        st.caption("🔒 Prototype mode: Passwords are simulated and not stored in plain text in database.")
        
        if st.button("Create Account & Continue", type="primary", use_container_width=True):
            if not new_username.strip():
                st.error("Username is required.")
            else:
                existing_users = queries.get_all_users()
                if any(u["username"].lower() == new_username.strip().lower() for u in existing_users):
                    st.error("This username is already taken. Please choose another one.")
                else:
                    # Create user
                    try:
                        user_id = queries.create_user(new_username.strip(), new_email.strip() or None)
                        st.session_state.current_user_id = user_id
                        st.session_state.current_user_name = new_username.strip()
                        st.session_state.onboarding_step = True  # Trigger onboarding
                        st.success("Account created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating account: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

def render_onboarding():
    """
    Renders the lightweight onboarding questionnaire.
    """
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2>🌱 Tell us about yourself</h2>", unsafe_allow_html=True)
    st.write("We customize descriptions to match your background. Let's make learning fit you!")
    
    st.markdown("---")
    
    # 1. Learner type
    st.markdown("**What type of learner are you?**")
    learner_options = {
        "🌱 Start from basics": ("beginner", "analogical"),
        "📘 I know the basics": ("intermediate", "practical"),
        "🚀 Give me deeper explanations": ("advanced", "technical"),
        "🤷 Let AI figure it out": ("beginner", "analogical")
    }
    learner_choice = st.radio(
        "Select your preference", 
        list(learner_options.keys()), 
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Field of study (Optional)
    st.markdown("**What are you studying?** (Optional)")
    study_choice = st.selectbox(
        "Select one",
        ["Engineering", "School", "College", "Professional", "Other"],
        index=2
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_submit, col_skip = st.columns(2)
    
    with col_submit:
        if st.button("Save Preferences", type="primary", use_container_width=True):
            level, style = learner_options[learner_choice]
            queries.update_db_learner_profile(
                st.session_state.current_user_id,
                level,
                style
            )
            # Log initial seeder history for a better dashboard experience
            try:
                queries.update_mastery(st.session_state.current_user_id, "recursion", 0.3)
                queries.update_mastery(st.session_state.current_user_id, "git_version_control", 0.5)
            except:
                pass
            st.session_state.onboarding_step = False
            st.success("Preferences saved! Welcome aboard!")
            st.rerun()
            
    with col_skip:
        if st.button("Skip — I'll figure it out as we go", use_container_width=True):
            # Default preferences: beginner, analogical
            queries.update_db_learner_profile(
                st.session_state.current_user_id,
                "beginner",
                "analogical"
            )
            st.session_state.onboarding_step = False
            st.info("Onboarding skipped. Learning profile set to default.")
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
