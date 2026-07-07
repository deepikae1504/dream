"""
pages/04_🗺️_Roadmap_Generator.py
"""
import streamlit as st
import json
from agents.roadmap_planner import RoadmapPlannerAgent
from database import db
from utils.session import init_session, login_gate
from utils.exporters import roadmap_to_markdown
from utils.ui_components import (apply_styles, page_header, progress_timeline,
                                  PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD)

def render():
    init_session()
    apply_styles()
    page_header("Roadmap Generator", "Your personalized step-by-step career plan",
                "Roadmap Planner Agent")

    if not login_gate("Roadmap Generator"):
        return

    uid = st.session_state.user_id
    user = db.get_user(uid)
    gap = st.session_state.get("skill_gap", {})
    goal = db.get_active_goal(uid)

    # Settings
    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
    border-radius:16px;padding:1.5rem;margin-bottom:1.5rem">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        daily_hours = st.slider("Daily study hours", 1, 8, 2)
    with col2:
        career_target = st.text_input("Target Career", value=user.get("dream_career",""))
    with col3:
        st.markdown(f"<br><p style='color:{TEXT_MUTED}'>Readiness: <strong>{gap.get('readiness_score',0)}%</strong></p>",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗺️ Generate My Personalized Roadmap", use_container_width=True):
            if not career_target:
                st.error("Please set your target career first.")
            else:
                agent = RoadmapPlannerAgent()
                with st.spinner("Roadmap Planner Agent is designing your journey..."):
                    try:
                        roadmap = agent.create_roadmap(
                            career_target, gap, user, daily_hours, uid)
                        st.session_state["roadmap"] = roadmap

                        goal_id = st.session_state.get("active_goal_id")
                        if not goal_id and goal:
                            goal_id = goal["id"]

                        db.save_roadmap(
                            uid, goal_id or 1,
                            json.dumps(roadmap.get("plan_30_day",{})),
                            json.dumps(roadmap.get("plan_90_day",{})),
                            json.dumps(roadmap.get("plan_6_month",{})),
                            json.dumps(roadmap.get("plan_1_year",{})),
                            roadmap.get("key_milestones",[])
                        )
                        st.success("✅ Roadmap generated!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col2:
        saved_rm = db.get_latest_roadmap(uid)
        if saved_rm:
            if st.button("📂 Load Saved Roadmap", use_container_width=True):
                roadmap = {
                    "plan_30_day": json.loads(saved_rm.get("plan_30_day","{}") or "{}"),
                    "plan_90_day": json.loads(saved_rm.get("plan_90_day","{}") or "{}"),
                    "plan_6_month": json.loads(saved_rm.get("plan_6_month","{}") or "{}"),
                    "plan_1_year": json.loads(saved_rm.get("plan_1_year","{}") or "{}"),
                    "key_milestones": json.loads(saved_rm.get("milestones","[]") or "[]"),
                }
                st.session_state["roadmap"] = roadmap
                st.rerun()

    roadmap = st.session_state.get("roadmap")
    if not roadmap:
        st.info("Click **Generate My Personalized Roadmap** to create your plan.")
        return

    if "raw" in roadmap:
        st.markdown(roadmap["raw"])
        return

    # ── Display roadmap ───────────────────────────────────────────────────────
    st.markdown(f"## {roadmap.get('roadmap_title','Your Career Roadmap')}")

    plan_colors = {
        "plan_30_day":  (PRIMARY,   "30 Days",  "🌱", "Foundation"),
        "plan_90_day":  (SECONDARY, "90 Days",  "🔥", "Core Skills"),
        "plan_6_month": (ACCENT,    "6 Months", "🚀", "Portfolio"),
        "plan_1_year":  ("#FFB84D", "1 Year",   "🏆", "Job Ready"),
    }

    tabs = st.tabs(["🌱 30 Days", "🔥 90 Days", "🚀 6 Months", "🏆 1 Year",
                    "📅 Weekly Schedule", "🗓️ Milestones"])

    plans = ["plan_30_day","plan_90_day","plan_6_month","plan_1_year"]
    for tab, plan_key in zip(tabs[:4], plans):
        plan = roadmap.get(plan_key, {})
        color, label, icon, theme = plan_colors[plan_key]
        with tab:
            if not plan:
                st.info("No data for this phase yet.")
                continue

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{color}20,{color}08);
            border:1px solid {color}40;border-radius:16px;padding:1.5rem;margin-bottom:1rem">
                <h3 style="margin:0;color:{color}">{icon} {plan.get('theme', theme)}</h3>
                <p style="color:{TEXT_MUTED};margin:0.5rem 0 0">
                    {plan.get('milestone', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🎯 Goals**")
                for g in plan.get("goals",[]):
                    st.markdown(f"• {g}")

                resources_key = "key_resources" if plan_key != "plan_1_year" else "goal"
                for r in plan.get(resources_key,[]):
                    st.markdown(f"📚 {r}")

            with col2:
                if "daily_tasks" in plan:
                    st.markdown("**⚡ Daily Focus**")
                    for t in plan.get("daily_tasks",[]):
                        st.markdown(f"✅ {t}")
                if "projects_to_build" in plan:
                    st.markdown("**🔨 Projects to Build**")
                    for p in plan.get("projects_to_build",[]):
                        st.markdown(f"🔨 {p}")
                if "portfolio_items" in plan:
                    st.markdown("**📁 Portfolio Items**")
                    for item in plan.get("portfolio_items",[]):
                        st.markdown(f"📁 {item}")
                if "expected_outcome" in plan:
                    st.markdown(f"**🏆 Expected Outcome:** {plan.get('expected_outcome','')}")
                    st.markdown(f"**💰 Salary Target:** {plan.get('salary_expectation','')}")

    # Weekly schedule tab
    with tabs[4]:
        schedule = roadmap.get("weekly_schedule", {})
        if schedule:
            days_order = ["monday","tuesday","wednesday","thursday","friday","weekend"]
            day_icons = {"monday":"Mon 🔵","tuesday":"Tue 🟢","wednesday":"Wed 🟣",
                         "thursday":"Thu 🟡","friday":"Fri 🔴","weekend":"Weekend 🎯"}
            cols = st.columns(3)
            for i, day in enumerate(days_order):
                if day in schedule:
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
                        border-radius:12px;padding:1rem;margin:0.3rem 0">
                            <div style="font-weight:700;margin-bottom:0.5rem">{day_icons.get(day,day.title())}</div>
                            <div style="color:{TEXT_MUTED};font-size:0.9rem">{schedule[day]}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Generate a roadmap to see weekly schedule.")

    # Milestones tab
    with tabs[5]:
        milestones = roadmap.get("key_milestones", [])
        if isinstance(milestones, str):
            try:
                milestones = json.loads(milestones)
            except Exception:
                milestones = []
        if milestones:
            progress_timeline(milestones)
        else:
            st.info("No milestones found. Generate a roadmap first.")

    # Download roadmap as text
    st.markdown("<br>", unsafe_allow_html=True)
    roadmap_text = roadmap_to_markdown(roadmap, user.get("name","User"), career_target)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download Roadmap (Markdown)", roadmap_text,
                           file_name="career_roadmap.md", mime="text/markdown",
                           use_container_width=True)
    with col2:
        if st.button("▶️ Next: Learning Resources", use_container_width=True):
            st.switch_page("pages/05_📚_Learning_Hub.py")


if __name__ == "__main__":
    from utils.sidebar import render_sidebar
    render_sidebar()
    render()
