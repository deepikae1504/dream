"""
pages/05_📚_Learning_Hub.py
"""
import streamlit as st
import json
from agents.learning_coach import LearningCoachAgent
from database import db
from utils.session import init_session, login_gate
from utils.validators import validate_progress_log
from utils.ui_components import (apply_styles, page_header, metric_card,
                                  PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD)
from config.constants import PLATFORM_ICONS, ACTIVITY_TYPES

def get_icon(platform: str) -> str:
    low = platform.lower()
    for k, v in PLATFORM_ICONS.items():
        if k in low:
            return v
    return PLATFORM_ICONS["default"]

def render():
    init_session()
    apply_styles()
    page_header("Learning Hub", "Curated resources and projects for your career path",
                "Learning Coach Agent")

    if not login_gate("Learning Hub"):
        return

    uid = st.session_state.user_id
    user = db.get_user(uid)
    gap = st.session_state.get("skill_gap", {})

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤖 Get AI-Curated Resources", use_container_width=True):
            if not gap:
                st.warning("Please complete Skill Assessment first.")
            else:
                agent = LearningCoachAgent()
                with st.spinner("Learning Coach Agent is finding the best resources..."):
                    try:
                        resources = agent.recommend_resources(
                            gap, user.get("dream_career",""), uid)
                        st.session_state["learning_resources"] = resources
                        # Save resources to DB
                        flat_resources = []
                        for path in resources.get("learning_path",[]):
                            for r in path.get("resources",[]):
                                flat_resources.append({
                                    "skill": path.get("skill",""),
                                    "type": r.get("type","course"),
                                    "title": r.get("title",""),
                                    "url": r.get("url",""),
                                    "platform": r.get("platform",""),
                                    "free": r.get("free", True),
                                    "priority": path.get("priority",1),
                                })
                        db.save_resources(uid, flat_resources)
                        st.success("✅ Resources loaded!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col2:
        saved = db.get_resources(uid)
        if saved:
            if st.button("📂 Load Saved Resources", use_container_width=True):
                st.info(f"You have {len(saved)} saved resources. Showing below.")

    resources = st.session_state.get("learning_resources")
    saved_resources = db.get_resources(uid)

    if not resources and not saved_resources:
        st.info("Complete Skill Assessment and click **Get AI-Curated Resources** to see your personalized learning plan.")

        # Generic popular resources
        st.markdown("### 🌟 Popular Free Resources")
        popular = [
            ("freeCodeCamp", "Full-stack web dev & Python", "https://freecodecamp.org", "💻", True),
            ("fast.ai", "Practical Deep Learning (free)", "https://fast.ai", "⚡", True),
            ("CS50 Harvard", "Best intro to CS", "https://cs50.harvard.edu", "🔴", True),
            ("Google ML Crash Course", "Machine Learning basics", "https://developers.google.com/machine-learning/crash-course", "🔵", True),
            ("Kaggle Learn", "Data science micro-courses", "https://kaggle.com/learn", "📊", True),
            ("The Odin Project", "Full-stack web development", "https://theodinproject.com", "⚔️", True),
        ]
        cols = st.columns(3)
        for i, (name, desc, url, icon, free) in enumerate(popular):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
                border-radius:12px;padding:1rem;margin:0.3rem 0">
                    <div style="font-size:1.5rem">{icon}</div>
                    <div style="font-weight:600;margin:0.3rem 0">{name}</div>
                    <div style="color:{TEXT_MUTED};font-size:0.8rem;margin-bottom:0.5rem">{desc}</div>
                    <div style="color:{SECONDARY};font-size:0.75rem">✅ FREE</div>
                </div>
                """, unsafe_allow_html=True)
        return

    # ── AI-recommended resources ───────────────────────────────────────────────
    if resources and "raw" not in resources:
        # Quick stats
        all_rs = [r for path in resources.get("learning_path",[])
                  for r in path.get("resources",[])]
        free_count = sum(1 for r in all_rs if r.get("free", True))

        col1, col2, col3, col4 = st.columns(4)
        with col1: metric_card("Learning Paths", str(len(resources.get("learning_path",[]))), icon="🗺️")
        with col2: metric_card("Total Resources", str(len(all_rs)), icon="📚")
        with col3: metric_card("Free Resources", str(free_count), icon="🆓")
        with col4: metric_card("YouTube Channels", str(len(resources.get("youtube_channels",[]))), icon="▶️")

        # Daily plan
        daily = resources.get("daily_learning_plan",{})
        if daily:
            st.markdown("### ⏰ Your Daily Learning Routine")
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div style="background:{BG_CARD};border-radius:12px;padding:1rem;text-align:center">
                    <div style="font-size:1.5rem">🌅</div>
                    <div style="font-weight:600">Morning</div>
                    <div style="color:{TEXT_MUTED};font-size:0.85rem">{daily.get('morning','')}</div>
                </div>""", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div style="background:{BG_CARD};border-radius:12px;padding:1rem;text-align:center">
                    <div style="font-size:1.5rem">💻</div>
                    <div style="font-weight:600">Main Session</div>
                    <div style="color:{TEXT_MUTED};font-size:0.85rem">{daily.get('main_session','')}</div>
                </div>""", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div style="background:{BG_CARD};border-radius:12px;padding:1rem;text-align:center">
                    <div style="font-size:1.5rem">🌙</div>
                    <div style="font-weight:600">Evening</div>
                    <div style="color:{TEXT_MUTED};font-size:0.85rem">{daily.get('evening','')}</div>
                </div>""", unsafe_allow_html=True)

        # Learning paths
        st.markdown("### 📚 Your Personalized Learning Path")
        for path in resources.get("learning_path",[]):
            skill = path.get("skill","")
            priority = path.get("priority",1)

            with st.expander(f"{'🔴' if priority == 1 else '🟡' if priority == 2 else '🟢'} Priority {priority}: {skill}", expanded=(priority == 1)):
                # Resources
                path_resources = path.get("resources",[])
                if path_resources:
                    st.markdown("**📖 Recommended Courses & Resources:**")
                    for r in path_resources:
                        platform = r.get("platform","")
                        icon = get_icon(platform)
                        free_badge = f'<span style="background:rgba(0,212,170,0.15);color:{SECONDARY};border-radius:10px;padding:0.1rem 0.5rem;font-size:0.7rem;margin-left:0.5rem">FREE</span>' if r.get("free") else ''
                        url = r.get("url","")
                        link = f'<a href="{url}" target="_blank" style="color:{PRIMARY}">→ Open</a>' if url and url.startswith("http") else ""

                        st.markdown(f"""
                        <div style="background:rgba(108,99,255,0.05);border:1px solid rgba(108,99,255,0.1);
                        border-radius:8px;padding:0.8rem;margin:0.3rem 0">
                            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                                <div>
                                    <span>{icon} <strong>{r.get('title','')}</strong>{free_badge}</span>
                                    <div style="color:{TEXT_MUTED};font-size:0.8rem;margin-top:0.2rem">
                                        {platform} · {r.get('duration','')} · ⭐ {r.get('rating','')}
                                    </div>
                                    <div style="color:{TEXT_MUTED};font-size:0.8rem">{r.get('why_recommended','')}</div>
                                </div>
                                <div>{link}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Projects
                projects = path.get("projects",[])
                if projects:
                    st.markdown("**🔨 Practice Projects:**")
                    for p in projects:
                        diff = p.get("difficulty","Intermediate")
                        diff_color = SECONDARY if diff == "Beginner" else PRIMARY if diff == "Intermediate" else ACCENT
                        st.markdown(f"""
                        <div style="border-left:3px solid {diff_color};padding-left:1rem;margin:0.5rem 0">
                            <strong>{p.get('title','')}</strong>
                            <span style="color:{diff_color};font-size:0.75rem;margin-left:0.5rem">{diff}</span>
                            <div style="color:{TEXT_MUTED};font-size:0.85rem">{p.get('description','')}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # YouTube channels
        channels = resources.get("youtube_channels",[])
        if channels:
            st.markdown("### ▶️ YouTube Channels to Follow")
            cols = st.columns(3)
            for i, ch in enumerate(channels):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="background:{BG_CARD};border-radius:10px;padding:0.8rem;margin:0.2rem;
                    border:1px solid rgba(255,0,0,0.2)">
                        ▶️ {ch}
                    </div>
                    """, unsafe_allow_html=True)

        # Communities
        communities = resources.get("communities_to_join",[])
        if communities:
            st.markdown("### 🤝 Communities to Join")
            for c in communities:
                st.markdown(f"• 🌐 {c}")

    # Log progress button
    st.markdown("---")
    st.markdown("### ✅ Log Today's Learning")
    with st.form("log_learning"):
        col1, col2 = st.columns(2)
        with col1:
            activity = st.selectbox("Activity", ACTIVITY_TYPES)
            hours = st.number_input("Hours spent", 0.0, 12.0, 1.0, 0.5)
        with col2:
            desc = st.text_area("What did you learn?", height=80,
                                placeholder="Briefly describe what you studied...")
            milestone = st.checkbox("Completed a milestone today 🏆")

        if st.form_submit_button("💾 Log Progress", use_container_width=True):
            valid, err = validate_progress_log(desc, hours)
            if not valid:
                st.error(err)
            else:
                db.log_progress(uid, activity, desc, hours, milestone)
                st.success("✅ Progress logged!")
                st.balloons()


if __name__ == "__main__":
    from utils.sidebar import render_sidebar
    render_sidebar()
    render()
