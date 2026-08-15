"""
Student Dashboard Page
Owner: Member 2 (UI/UX) - Enhanced for Hackathon Reliability & Clean Learning Metrics
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
    raw_mastery = queries.get_topic_mastery(user_id) or []
    raw_history = queries.get_learning_history(user_id) or []
    raw_refresh = queries.get_smart_refresh_history(user_id) or []
    profile = queries.get_db_learner_profile(user_id) or {}
    
    # Standardize data into clean dictionaries for calculations
    db_mastery = []
    for t in raw_mastery:
        if hasattr(t, "to_dict"):
            db_mastery.append(t.to_dict())
        elif isinstance(t, dict):
            db_mastery.append(t)
        else:
            db_mastery.append({
                "title": getattr(t, "topic_name", getattr(t, "topic_id", "Concept")),
                "mastery_score": getattr(t, "mastery_score", 0.0),
                "category": getattr(t, "subject", "Computer Science"),
                "status": getattr(t, "status", "learning")
            })

    db_history = []
    for h in raw_history:
        if hasattr(h, "to_dict"):
            db_history.append(h.to_dict())
        elif isinstance(h, dict):
            db_history.append(h)
        else:
            db_history.append({
                "title": getattr(h, "topic_name", "Concept"),
                "created_at": getattr(h, "started_at", getattr(h, "created_at", "Recently")),
                "explanation_level": getattr(h, "explanation_level", "beginner"),
                "time_spent_seconds": getattr(h, "duration", 0)
            })

    # 1. PROFILE HEADER CARD (Without internal implementation details like 'Style')
    level = (profile.get("estimated_level") or profile.get("preferred_level") or "beginner").upper()
    user_name = st.session_state.get("current_user_name", "Student")
    
    st.markdown(f"""
    <div class='glass-card' style='margin-bottom: 20px;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h3 style='margin: 0; color: #4D96FF;'>👤 Student: {user_name}</h3>
                <p style='margin: 5px 0 0 0; color: #aaa;'>Empowering your learning journey with concept bridges.</p>
            </div>
            <div>
                <span class='onboarding-badge' style='font-size: 0.9rem; padding: 6px 14px;'>Estimated Level: {level}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # If database has no entries yet, supplement with initial sample concepts
    if not db_mastery:
        db_mastery = [
            {"title": "Recursion & The Call Stack", "mastery_score": 0.45, "category": "Computer Science", "status": "learning"},
            {"title": "Binary Search", "mastery_score": 0.85, "category": "Algorithms", "status": "mastered"},
            {"title": "Graph Coloring", "mastery_score": 0.20, "category": "Graph Theory", "status": "struggling"},
            {"title": "Hash Table / Hash Map", "mastery_score": 0.70, "category": "Data Structures", "status": "learning"}
        ]

    # Calculate metrics
    num_topics = len(db_mastery)
    mastery_percentages = [float(t.get("mastery_score", 0.0)) * 100 for t in db_mastery]
    avg_mastery = sum(mastery_percentages) / num_topics if num_topics > 0 else 0.0
    study_seconds = sum([int(h.get("time_spent_seconds", 0) or 0) for h in db_history]) if db_history else 300
    study_mins = max(5, study_seconds // 60)
    breaks_taken = len(raw_refresh) if raw_refresh else 0

    # Categorize Strong vs Weak Topics
    strong_topics = [t["title"] for t in db_mastery if t.get("mastery_score", 0.0) >= 0.75]
    improving_topics = [t["title"] for t in db_mastery if 0.40 <= t.get("mastery_score", 0.0) < 0.75]
    weak_topics = [t["title"] for t in db_mastery if t.get("mastery_score", 0.0) < 0.40]

    # RENDER METRIC BADGES
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f"""
        <div style='background: rgba(77, 150, 255, 0.1); border: 1px solid rgba(77, 150, 255, 0.25); border-radius: 12px; padding: 16px; text-align: center;'>
            <h5 style='margin: 0; color: #888; font-size: 0.85rem;'>OVERALL PROGRESS</h5>
            <h2 style='margin: 8px 0 0 0; color: #4D96FF;'>{avg_mastery:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 12px; padding: 16px; text-align: center;'>
            <h5 style='margin: 0; color: #888; font-size: 0.85rem;'>STRONG TOPICS</h5>
            <h2 style='margin: 8px 0 0 0; color: #10B981;'>{len(strong_topics)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"""
        <div style='background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 12px; padding: 16px; text-align: center;'>
            <h5 style='margin: 0; color: #888; font-size: 0.85rem;'>TOPICS TO IMPROVE</h5>
            <h2 style='margin: 8px 0 0 0; color: #F59E0B;'>{len(weak_topics)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col_m4:
        st.markdown(f"""
        <div style='background: rgba(167, 139, 250, 0.1); border: 1px solid rgba(167, 139, 250, 0.25); border-radius: 12px; padding: 16px; text-align: center;'>
            <h5 style='margin: 0; color: #888; font-size: 0.85rem;'>REFRESH BREAKS</h5>
            <h2 style='margin: 8px 0 0 0; color: #A78BFA;'>{breaks_taken}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. CHARTS SECTION
    st.markdown("### 📈 Topic Mastery & Distribution")
    col_chart1, col_chart2 = st.columns([5, 4])
    
    with col_chart1:
        df_mastery = pd.DataFrame(db_mastery)
        df_mastery["mastery_pct"] = df_mastery["mastery_score"] * 100
        
        if HAS_PLOTLY:
            fig_mastery = px.bar(
                df_mastery,
                x="mastery_pct",
                y="title",
                orientation="h",
                color="category",
                title="Topic Mastery Level (%)",
                labels={"mastery_pct": "Mastery (%)", "title": "Topic"},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_mastery.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="Inter",
                font_color="#FFF",
                title_font_family="Outfit",
                title_font_size=15,
                xaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
                yaxis=dict(gridcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_mastery, use_container_width=True)
        else:
            st.subheader("Topic Mastery Progress (%)")
            chart_df = df_mastery.set_index("title")[["mastery_pct"]]
            st.bar_chart(chart_df)
        
    with col_chart2:
        # Mastery status breakdown
        status_labels = []
        for t in db_mastery:
            score = t.get("mastery_score", 0.0)
            if score >= 0.75:
                status_labels.append("Mastered")
            elif score >= 0.40:
                status_labels.append("In Progress")
            else:
                status_labels.append("Needs Review")
        
        df_mastery["status_label"] = status_labels
        status_counts = df_mastery["status_label"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        if HAS_PLOTLY:
            color_map = {"Mastered": "#10B981", "In Progress": "#3B82F6", "Needs Review": "#F59E0B"}
            fig_pie = px.pie(
                status_counts,
                values="Count",
                names="Status",
                title="Learning Retention Breakdown",
                color="Status",
                color_discrete_map=color_map
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Inter",
                font_color="#FFF",
                title_font_family="Outfit",
                title_font_size=15,
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.subheader("Retention Status")
            st.dataframe(status_counts)

    # 3. TOPICS AUDIT (STRONG VS WEAK) & RECOMMENDATIONS
    st.markdown("---")
    col_breakdown, col_rec = st.columns([1, 1])

    with col_breakdown:
        st.markdown("### 📋 Topic Health Breakdown")
        
        if strong_topics:
            st.markdown(f"**🟢 Strong Concepts ({len(strong_topics)}):**")
            st.write(", ".join([f"`{t}`" for t in strong_topics]))
            
        if improving_topics:
            st.markdown(f"**🟡 Learning in Progress ({len(improving_topics)}):**")
            st.write(", ".join([f"`{t}`" for t in improving_topics]))
            
        if weak_topics:
            st.markdown(f"**🔴 Topics Needing Reinforcement ({len(weak_topics)}):**")
            st.write(", ".join([f"`{t}`" for t in weak_topics]))

    with col_rec:
        st.markdown("### 🎯 Recommended Next Steps")
        st.caption("AI-curated learning pathway based on your mastery profile:")
        
        current_topic = db_history[0]["title"] if db_history else "Recursion"
        recs = recommendations.get_next_recommendations(user_id, current_topic)
        
        for idx, rec in enumerate(recs):
            st.markdown(f"""
            <div class='glass-card' style='padding: 14px; margin-bottom: 10px;'>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <strong>💡 {rec}</strong>
                    <span style='color: #4D96FF; font-size: 0.8rem; font-weight:600;'>Recommended</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Study '{rec}'", key=f"rec_btn_{idx}", use_container_width=True):
                st.session_state.load_recommended_topic = rec
                st.session_state.navigation_selection = "📖 Learning Hub"
                st.rerun()

    # 4. RECENT ACTIVITY
    st.markdown("---")
    st.markdown("### 📜 Recent Learning Activity")
    if db_history:
        for idx, hist in enumerate(db_history[:5]):
            time_str = hist.get("created_at", "Recent")
            if " " in time_str:
                time_str = time_str.split(" ")[0]
            level_badge = hist.get("explanation_level", "beginner").upper()
            st.markdown(f"""
            <div class='glass-card' style='padding: 12px; margin-bottom: 8px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong>{hist.get('title', 'Concept Explored')}</strong>
                        <span style='font-size: 0.8rem; color: #888; margin-left: 12px;'>Date: {time_str}</span>
                    </div>
                    <div>
                        <span class='onboarding-badge' style='margin: 0; font-size: 0.75rem;'>{level_badge}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No study sessions logged yet. Head over to the **Learning Hub** to start exploring concepts!")
