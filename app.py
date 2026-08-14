"""
ConceptBridge AI - Main Application Entry Point
Tagline: From "I don't understand" to "Oh, it's that easy!"

This is the primary entry point for the Streamlit web application.
It integrates frontend views, the AI teaching engine, database operations,
and the Smart Refresh subsystem following a strict separation of concerns.
"""

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit Page Configuration
st.set_page_config(
    page_title="ConceptBridge AI",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🌉 ConceptBridge AI")
    st.caption('From *"I don\'t understand"* to *"Oh, it\'s that easy!"*')

    st.markdown("---")
    st.info(
        "🚀 **ConceptBridge AI Repository Initialized!**\n\n"
        "Welcome to the 4-member hackathon project workspace. "
        "Feature branches are configured for each subsystem:\n"
        "- `feature/ui`: Frontend, UI/UX, pages & components\n"
        "- `feature/ai-teaching`: Teaching engine, learner profiles, misconceptions & recommendations\n"
        "- `feature/database`: Schema, queries, user records, topic mastery & history\n"
        "- `feature/smart-refresh`: 5-minute micro-break activities & fatigue monitoring\n\n"
        "Please follow the Git workflow outlined in the README."
    )

    # Placeholder container layout
    with st.sidebar:
        st.header("Navigation")
        st.write("• Learning Hub")
        st.write("• Student Dashboard")
        st.write("• Smart Refresh (Break)")
        st.write("• Settings")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("💡 Concept Explorer")
        st.text_input("Enter a concept to learn (e.g. Recursion, Neural Networks, PCA):", placeholder="Type a concept...")

    with col2:
        st.subheader("⚡ Smart Refresh")
        st.write("Take a productive micro-break (max 5 minutes).")
        st.button("Start 5-Min Smart Refresh")

if __name__ == "__main__":
    main()
