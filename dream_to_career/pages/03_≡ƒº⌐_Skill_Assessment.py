"""
pages/03_🧩_Skill_Assessment.py
"""
import streamlit as st
import json
import plotly.graph_objects as go
from agents.skill_gap import SkillGapAgent
from database import db
from utils.session import init_session, login_gate
from utils.ui_components import (apply_styles, page_header, metric_card,
                                  skill_chips, score_gauge, radar_chart,
                                  PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD)

from config.constants import SKILL_CATEGORIES

def render():
    init_session()
    apply_styles()
    page_header("Skill Assessment", "Identify exactly where you are and what you need",
                "Skill Gap Agent")

    if not login_gate("Skill Assessment"):
        return

    uid = st.session_state.user_id
    user = db.get_user(uid)
    existing_skills = db.get_skills(uid)
    goal = db.get_active_goal(uid)

    # ── Step 1: Enter current skills ──────────────────────────────────────────
    st.markdown("### Step 1: Rate Your Current Skills")
    st.markdown(f"<p style='color:{TEXT_MUTED}'>Rate each skill from 1 (Beginner) to 5 (Expert). Leave at 0 if you don't know it.</p>",
                unsafe_allow_html=True)

    if "skill_ratings" not in st.session_state:
        saved = {s["skill_name"]: s["proficiency_level"] for s in existing_skills}
        st.session_state.skill_ratings = saved

    tabs = st.tabs(list(SKILL_CATEGORIES.keys()))
    for tab, (category, skills) in zip(tabs, SKILL_CATEGORIES.items()):
        with tab:
            cols = st.columns(2)
            for i, skill in enumerate(skills):
                with cols[i % 2]:
                    val = st.slider(
                        skill,
                        0, 5,
                        st.session_state.skill_ratings.get(skill, 0),
                        key=f"skill_{skill}"
                    )
                    st.session_state.skill_ratings[skill] = val

    # Custom skills
    st.markdown("### Step 2: Add Any Other Skills")
    custom = st.text_input("Type additional skills (comma-separated)",
                           placeholder="e.g. LangChain, FastAPI, MongoDB")

    # Instant local preview (no API call) if we already have required skills
    if goal and goal.get("required_skills"):
        try:
            req_preview = json.loads(goal["required_skills"])
            from tools.assessment_tools import calculate_local_readiness
            local_score = calculate_local_readiness(
                st.session_state.skill_ratings, req_preview
            )
            st.caption(f"⚡ Quick local estimate (no AI call): **{local_score}%** readiness — "
                      f"click below for the full AI-powered breakdown.")
        except Exception:
            pass

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Skills & Analyze Gaps", use_container_width=True):
            skills_list = [
                {"name": skill, "category": cat, "level": lvl}
                for cat, skills_grp in SKILL_CATEGORIES.items()
                for skill in skills_grp
                if (lvl := st.session_state.skill_ratings.get(skill, 0)) > 0
            ]
            if custom:
                for cs in custom.split(","):
                    cs = cs.strip()
                    if cs:
                        skills_list.append({"name": cs, "category": "Other", "level": 3})

            db.save_skills(uid, skills_list)

            required = []
            if goal and goal.get("required_skills"):
                try:
                    required = json.loads(goal["required_skills"])
                except Exception:
                    required = []

            agent = SkillGapAgent()
            with st.spinner("Skill Gap Agent is analyzing your profile..."):
                try:
                    gap_result = agent.assess_gaps(
                        user.get("dream_career","AI Engineer"),
                        skills_list, required, uid
                    )
                    st.session_state["skill_gap"] = gap_result
                    st.success("✅ Skill gap analysis complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        if existing_skills and st.button("📊 Load Previous Assessment", use_container_width=True):
            if "skill_gap" not in st.session_state:
                st.info("Re-run the analysis to see results.")
            st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    gap = st.session_state.get("skill_gap")
    if not gap or "raw" in gap:
        if gap and "raw" in gap:
            st.markdown(gap["raw"])
        return

    st.markdown("---")
    st.markdown("## 📊 Your Skill Gap Report")

    col1, col2, col3 = st.columns(3)
    with col1:
        score = gap.get("readiness_score", 0)
        st.plotly_chart(score_gauge(score, "Readiness Score"), use_container_width=True)
    with col2:
        metric_card("Readiness Level", gap.get("readiness_level","Beginner"), icon="📊")
        metric_card("Timeline", f"{gap.get('estimated_readiness_timeline_months',12)} months",
                    icon="⏱️")
    with col3:
        metric_card("Skill Gaps Found", str(len(gap.get("skill_gaps",[]))), icon="🎯")
        metric_card("Strengths", str(len(gap.get("strengths",[]))), icon="💪")

    # Gap summary
    st.markdown(f"""
    <div style="background:rgba(108,99,255,0.08);border-left:4px solid {PRIMARY};
    border-radius:0 12px 12px 0;padding:1rem 1.5rem;margin:1rem 0">
        <strong>Gap Summary:</strong> {gap.get('gap_summary','')}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💪 Your Strengths")
        for s in gap.get("strengths", []):
            name = s.get("skill","") if isinstance(s, dict) else s
            note = s.get("note","") if isinstance(s, dict) else ""
            st.markdown(f"""
            <div style="background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.2);
            border-radius:8px;padding:0.6rem 1rem;margin:0.3rem 0">
                <strong style="color:{SECONDARY}">✅ {name}</strong>
                <div style="color:{TEXT_MUTED};font-size:0.85rem">{note}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### ⚡ Quick Wins (Learn in < 2 weeks)")
        for qw in gap.get("quick_wins",[]):
            st.markdown(f"⚡ {qw}")

    with col2:
        st.markdown("### 🎯 Skill Gaps (Priority Order)")
        priority_colors = {"Critical": ACCENT, "High": "#FFB84D",
                           "Medium": PRIMARY, "Low": TEXT_MUTED}
        for g in gap.get("skill_gaps", []):
            skill = g.get("skill","") if isinstance(g, dict) else g
            priority = g.get("priority","Medium") if isinstance(g, dict) else "Medium"
            weeks = g.get("effort_weeks",4) if isinstance(g, dict) else 4
            color = priority_colors.get(priority, TEXT_MUTED)
            st.markdown(f"""
            <div style="background:rgba(255,101,132,0.05);border:1px solid rgba(255,101,132,0.15);
            border-radius:8px;padding:0.6rem 1rem;margin:0.3rem 0;
            border-left:3px solid {color}">
                <div style="display:flex;justify-content:space-between">
                    <strong>{skill}</strong>
                    <span style="color:{color};font-size:0.8rem">{priority}</span>
                </div>
                <div style="color:{TEXT_MUTED};font-size:0.8rem">~{weeks} weeks to learn</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 🚀 Start With These First")
    for skill in gap.get("immediate_focus",[]):
        st.markdown(f"▶️ **{skill}**")

    # Radar chart of current skills
    current_rated = [(skill, lvl) for skill, lvl in st.session_state.skill_ratings.items()
                     if lvl > 0][:8]
    if len(current_rated) >= 3:
        cats = [s[0] for s in current_rated]
        vals = [s[1] * 20 for s in current_rated]  # scale to 100
        st.plotly_chart(radar_chart(cats, vals, "Your Current Skill Profile"),
                        use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("▶️ Next: Generate My Roadmap", use_container_width=True):
        st.switch_page("pages/04_🗺️_Roadmap_Generator.py")


if __name__ == "__main__":
    from utils.sidebar import render_sidebar
    render_sidebar()
    render()
