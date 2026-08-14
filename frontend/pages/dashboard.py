"""
Student Dashboard Page
Owner: Member 2 (UI/UX)
"""

import streamlit as st
import pandas as pd
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
import database.queries as queries
import ai.recommendations as recommendations

def show():
    # Ensure user is logged in
    user_id = st.session_state.get("current_user_id")
    if not user_id:
        st.warning("🔒 Please log in or sign up first.")
        return

    st.markdown("<h2>📊 Student Learning Dashboard</h2>", unsafe_allow_html=True)
    st.write("Track your academic concept mastery, review history, and explore personalized study recommendations.")

    # Fetch real user data from DB
    db_mastery = queries.get_topic_mastery(user_id)
    db_history = queries.get_learning_history(user_id)
    db_refresh = queries.get_smart_refresh_history(user_id)
    profile = queries.get_db_learner_profile(user_id) or {}
    
    # 1. PROFILE HEADER CARD
    level = profile.get("estimated_level", "beginner").upper()
    style = profile.get("preferred_learning_style", "analogical").upper()
    
    st.markdown(f"""
    <div class='glass-card'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3 style='margin: 0; color: #4D96FF;'>👤 Student: {st.session_state.current_user_name}</h3>
                <p style='margin: 5px 0 0 0; color: #888;'>Ready to bridge the gap in your concepts today?</p>
            </div>
            <div>
                <span class='onboarding-badge'>Level: {level}</span>
                <span class='onboarding-badge' style='background: linear-gradient(135deg, #10B981 0%, #059669 100%);'>Style: {style}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # If database is empty, supplement with mock data for visual demonstration
    if not db_mastery:
        # Mock mastery data
        db_mastery = [
            {"title": "Recursion", "mastery_score": 0.35, "category": "Computer Science", "status": "learning"},
            {"title": "Git Version Control", "mastery_score": 0.65, "category": "Software Engineering", "status": "learning"},
            {"title": "Principal Component Analysis (PCA)", "mastery_score": 0.15, "category": "Data Science", "status": "learning"},
            {"title": "Neural Networks", "mastery_score": 0.0, "category": "Artificial Intelligence", "status": "not_started"}
        ]
    if not db_history:
        # Mock history data
        db_history = [
            {"title": "Git Version Control", "created_at": "2026-08-14 18:22:15", "explanation_level": "beginner"},
            {"title": "Recursion", "created_at": "2026-08-14 17:15:30", "explanation_level": "beginner"}
        ]

    # Calculate metrics
    num_topics = len(db_mastery)
    mastery_percentages = [float(t.get("mastery_score", 0)) * 100 for t in db_mastery]
    avg_mastery = sum(mastery_percentages) / num_topics if num_topics > 0 else 0
    study_seconds = sum([int(h.get("time_spent_seconds", 0)) for h in db_history]) if db_history else 0
    study_mins = max(5, study_seconds // 60)
    breaks_taken = len(db_refresh) if db_refresh else 1

    # RENDER METRIC BADGES
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f"""
        <div style='background: rgba(77, 150, 255, 0.1); border: 1px solid rgba(77, 150, 255, 0.2); border-radius: 12px; padding: 16px; text-align: center;'>
            <h5 style='margin: 0; color: #888; font-size: 0.9rem;'>TOPIC MASTERY</h5>
            <h2 style='margin: 8px 0 0 0; color: #4D96FF;'>{avg_mastery:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div style='background: rgba(107, 203, 119, 0.1); border: 1px solid rgba(107, 203, 119, 0.2); border-radius: 12px; padding: 16px; text-align: center;'>
            <h5 style='margin: 0; color: #888; font-size: 0.9rem;'>STUDY TIME</h5>
            <h2 style='margin: 8px 0 0 0; color: #6BCB77;'>{study_mins} mins</h2>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"""
        <div style='background: rgba(167, 139, 250, 0.1); border: 1px solid rgba(167, 139, 250, 0.2); border-radius: 12px; padding: 16px; text-align: center;'>
            <h5 style='margin: 0; color: #888; font-size: 0.9rem;'>REFRESH BREAKS</h5>
            <h2 style='margin: 8px 0 0 0; color: #A78BFA;'>{breaks_taken} taken</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. CHARTS SECTION
    st.markdown("### 📈 Mastery and Progress Visualizations")
    col_chart1, col_chart2 = st.columns([5, 4])
    
    with col_chart1:
        df_mastery = pd.DataFrame(db_mastery)
        df_mastery["mastery_pct"] = df_mastery["mastery_score"] * 100
        
        if HAS_PLOTLY:
            # Mastery Horizontal Bar Chart
            fig_mastery = px.bar(
                df_mastery,
                x="mastery_pct",
                y="title",
                orientation="h",
                color="category",
                title="Topic Mastery Progress (%)",
                labels={"mastery_pct": "Mastery Level", "title": "Concept"},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_mastery.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="Inter",
                font_color="#FFF",
                title_font_family="Outfit",
                title_font_size=16,
                xaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
                yaxis=dict(gridcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_mastery, use_container_width=True)
        else:
            st.subheader("Topic Mastery Progress (%)")
            chart_df = df_mastery.set_index("title")[["mastery_pct"]]
            st.bar_chart(chart_df)
        
    with col_chart2:
        if HAS_PLOTLY:
            status_counts = df_mastery["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            
            fig_pie = px.pie(
                status_counts,
                values="count",
                names="status",
                title="Comprehension Distribution",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Inter",
                font_color="#FFF",
                title_font_family="Outfit",
                title_font_size=16,
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.subheader("Comprehension Status")
            st.dataframe(df_mastery[["title", "status", "mastery_pct"]])

    # 3. RECOMMENDATIONS & HISTORY
    st.markdown("---")
    col_rec, col_hist = st.columns([1, 1])
    
    with col_rec:
        st.markdown("### 🎯 Recommended Next Topics")
        st.caption("AI curated prerequisite and deep-dive routes for your learning goals:")
        
        current_topic = db_history[0]["title"] if db_history else "Recursion"
        recs = recommendations.get_next_recommendations(user_id, current_topic)
        
        for idx, rec in enumerate(recs):
            st.markdown(f"""
            <div class='glass-card' style='padding: 16px; margin-bottom: 12px;'>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <strong>💡 {rec}</strong>
                    <span style='color: #4D96FF; font-size: 0.85rem; font-weight:600;'>Recommended</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Use columns to position buttons cleanly below markdown cards
            col_b1, col_spacer = st.columns([1, 2])
            with col_b1:
                if st.button(f"Study '{rec}'", key=f"rec_{idx}", use_container_width=True):
                    st.session_state.load_recommended_topic = rec
                    st.session_state.navigation_selection = "📖 Learning Hub"
                    st.rerun()

    with col_hist:
        st.markdown("### 📜 Recently Learned Topics")
        st.caption("Snapshots of your completed explanations and study dates:")
        
        for idx, hist in enumerate(db_history[:4]):
            time_str = hist.get("created_at", "Just now")
            # Parse database timestamp for display
            if " " in time_str:
                time_str = time_str.split(" ")[0]
            level_badge = hist.get("explanation_level", "beginner").upper()
            
            st.markdown(f"""
            <div class='glass-card' style='padding: 15px; margin-bottom: 12px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <div>
                        <strong>{hist.get('title', 'General Concept')}</strong><br>
                        <span style='font-size: 0.8rem; color: #888;'>Studied on: {time_str}</span>
                    </div>
                    <div>
                        <span class='onboarding-badge' style='margin: 0; font-size: 0.75rem;'>{level_badge}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
