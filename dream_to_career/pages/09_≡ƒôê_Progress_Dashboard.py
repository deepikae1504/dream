"""
pages/09_📈_Progress_Dashboard.py
Progress Dashboard — health scores, activity log, weekly plan, career summary.
"""
import streamlit as st
import json
from agents.accountability import AccountabilityAgent
from database import db
from tools.career_tools import build_progress_summary, streak_days
from utils.session import init_session, login_gate
from utils.ui_components import apply_styles, page_header, health_score_bars
from utils.charts import (
    score_gauge, health_history_chart, progress_line, skill_donut
)
from utils.exporters import progress_to_csv
from config.constants import ACTIVITY_TYPES, COLORS

P  = COLORS["primary"]
S  = COLORS["secondary"]
A  = COLORS["accent"]
MT = COLORS["text_muted"]
BC = COLORS["bg_card"]


def render():
    init_session()
    apply_styles()
    page_header(
        "Progress Dashboard",
        "Your weekly career health score, activity log, and improvement plan",
        "Accountability Agent",
    )

    if not login_gate("Progress Dashboard"):
        return

    uid  = st.session_state.user_id
    user = db.get_user(uid)
    career = user.get("dream_career", "your target career")

    # ── Top summary strip ─────────────────────────────────────────────────────
    summary = build_progress_summary(uid)

    c1, c2, c3, c4, c5 = st.columns(5)
    def _metric(col, title, value, icon):
        with col:
            st.markdown(f"""
            <div style="background:{BC};border:1px solid rgba(108,99,255,0.2);
            border-radius:12px;padding:1rem;text-align:center">
                <div style="font-size:1.3rem">{icon}</div>
                <div style="font-size:1.6rem;font-weight:700;
                color:{S}">{value}</div>
                <div style="color:{MT};font-size:0.75rem">{title}</div>
            </div>""", unsafe_allow_html=True)

    _metric(c1, "Hours (30d)",    summary["total_hours_30d"],     "⏱️")
    _metric(c2, "Active Days",    summary["active_days_30d"],      "📅")
    _metric(c3, "Streak",         f"{summary['streak']} days",     "🔥")
    _metric(c4, "Milestones",     summary["milestones_30d"],       "🏆")
    _metric(c5, "Interview Avg",  f"{summary['avg_interview']}/10","🎤")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Weekly Health Score ───────────────────────────────────────────────────
    st.markdown("### 📊 Weekly Career Health Score")

    health_rows = db.get_health_scores(uid, 10)
    current_health = health_rows[0] if health_rows else {}

    col_gauge, col_bars, col_gen = st.columns([1, 2, 1])

    with col_gauge:
        overall = current_health.get("overall_score", 0) if current_health else 0
        st.plotly_chart(score_gauge(overall, "Overall Health"), use_container_width=True)
        grade_color = S if overall >= 70 else (P if overall >= 40 else A)
        grade = current_health.get("grade","—") if current_health else "—"
        st.markdown(f"""
        <div style="text-align:center;margin-top:-1rem">
            <span style="font-size:2rem;font-weight:700;color:{grade_color}">{grade}</span>
            <span style="color:{MT};font-size:0.85rem"> / {career[:20]}</span>
        </div>""", unsafe_allow_html=True)

    with col_bars:
        if current_health:
            health_score_bars(current_health)
        else:
            st.info("No health score yet. Click **Generate** to get your first one.")

    with col_gen:
        if st.button("🔄 Generate\nHealth Score", use_container_width=True):
            agent = AccountabilityAgent()
            progress_logs = db.get_progress(uid, 30)
            interviews    = db.get_interviews(uid, 10)
            int_scores    = [i.get("overall_score", 0) for i in interviews]
            with st.spinner("Accountability Agent scoring your week..."):
                try:
                    result = agent.calculate_health_score(
                        progress_logs, int_scores, user, uid)
                    st.session_state["health_score"] = result
                    db.save_health_score(
                        uid,
                        result.get("learning_consistency", 0),
                        result.get("skill_development", 0),
                        result.get("project_building", 0),
                        result.get("interview_readiness", 0),
                        result.get("overall_score", 0),
                        json.dumps(result.get("insights", [])),
                    )
                    st.success("✅ Done!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # Insights / motivational message
    if current_health:
        insights = current_health.get("insights") or []
        if isinstance(insights, str):
            try: insights = json.loads(insights)
            except Exception: insights = [insights]

        msg = current_health.get("motivational_message", "")
        focus = current_health.get("this_week_focus", "")

        if msg:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(108,99,255,0.1),
            rgba(0,212,170,0.06));border:1px solid rgba(108,99,255,0.25);
            border-radius:14px;padding:1.2rem 1.5rem;margin:1rem 0">
                <div style="font-size:0.8rem;color:{MT};margin-bottom:0.3rem">
                    🤖 Accountability Agent
                </div>
                <em style="color:{S}">&ldquo;{msg}&rdquo;</em>
                {f'<div style="margin-top:0.8rem;font-weight:600">🎯 This week: {focus}</div>' if focus else ''}
            </div>""", unsafe_allow_html=True)

        if insights:
            st.markdown("**📋 Insights:**")
            for ins in insights:
                st.markdown(f"• {ins}")

    # Health history chart
    if len(health_rows) >= 2:
        st.markdown("### 📈 Health Score Trend")
        st.plotly_chart(health_history_chart(health_rows), use_container_width=True)

    st.markdown("---")

    # ── Weekly Plan ───────────────────────────────────────────────────────────
    st.markdown("### 📅 This Week's Plan")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("✨ Generate Weekly Plan", use_container_width=True):
            agent = AccountabilityAgent()
            roadmap = db.get_latest_roadmap(uid)
            plan_30 = {}
            if roadmap:
                try: plan_30 = json.loads(roadmap.get("plan_30_day","{}") or "{}")
                except Exception: pass
            h = st.session_state.get("health_score") or current_health or {}
            with st.spinner("Building your week..."):
                try:
                    weekly = agent.generate_weekly_plan(
                        h, {"plan_30_day": plan_30}, user, uid)
                    st.session_state["weekly_plan"] = weekly
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    weekly = st.session_state.get("weekly_plan")
    if weekly and "raw" not in weekly:
        daily_goals = weekly.get("daily_goals", [])
        if daily_goals:
            day_cols = st.columns(min(len(daily_goals), 7))
            colors = [P, S, A, "#A78BFA", "#34D399", "#F59E0B", "#EC4899"]
            for i, (col, day) in enumerate(zip(day_cols, daily_goals)):
                c = colors[i % len(colors)]
                with col:
                    st.markdown(f"""
                    <div style="background:{BC};border-top:3px solid {c};
                    border:1px solid {c}30;border-radius:10px;padding:0.8rem;
                    border-top-color:{c};border-top-width:3px">
                        <div style="font-weight:700;font-size:0.85rem;color:{c}">
                            {day.get('day','')}</div>
                        <div style="font-size:0.8rem;margin:0.3rem 0">
                            {day.get('primary_task','')}</div>
                        <div style="color:{MT};font-size:0.75rem">
                            {day.get('secondary_task','')}
                        </div>
                        <div style="color:{S};font-size:0.75rem;margin-top:0.3rem">
                            ⏱️ {day.get('hours',1)}h
                        </div>
                    </div>""", unsafe_allow_html=True)

        challenge = weekly.get("weekly_challenge","")
        reward    = weekly.get("reward","")
        if challenge:
            st.markdown(f"""
            <div style="background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.2);
            border-radius:10px;padding:0.8rem 1.2rem;margin-top:1rem">
                🏆 <strong>Weekly Challenge:</strong> {challenge}
                {f' · 🎁 <strong>Reward:</strong> {reward}' if reward else ''}
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Log today's activity ──────────────────────────────────────────────────
    st.markdown("### ✏️ Log Today's Activity")
    with st.form("log_progress_dash"):
        col1, col2 = st.columns(2)
        with col1:
            activity = st.selectbox("Activity type", ACTIVITY_TYPES)
            hours    = st.number_input("Hours", 0.0, 16.0, 1.0, 0.5)
        with col2:
            desc      = st.text_area("What did you do?", height=90,
                                     placeholder="Finished chapter 3 of fast.ai…")
            milestone = st.checkbox("Completed a milestone 🏆")

        if st.form_submit_button("💾 Save", use_container_width=True):
            if desc.strip() and hours > 0:
                db.log_progress(uid, activity, desc, hours, milestone)
                st.success("✅ Activity logged!")
                st.rerun()
            else:
                st.error("Please describe the activity and enter hours > 0.")

    # ── Activity history ──────────────────────────────────────────────────────
    st.markdown("### 📋 Activity History")
    logs = db.get_progress(uid, 30)
    if logs:
        # Hours per day line chart
        from collections import defaultdict
        daily: dict = defaultdict(float)
        for l in logs:
            daily[l.get("date","")] += float(l.get("hours_spent",0))
        sorted_days = sorted(daily.items())
        if len(sorted_days) >= 2:
            st.plotly_chart(
                progress_line(
                    [d[0] for d in sorted_days],
                    [d[1] for d in sorted_days],
                    label="Hours",
                    title="Daily Study Hours",
                    height=220,
                ),
                use_container_width=True,
            )

        # Table
        import pandas as pd
        df = pd.DataFrame(logs)[
            ["date","activity_type","description","hours_spent","milestone_completed"]
        ]
        df.columns = ["Date","Activity","Description","Hours","Milestone"]
        df["Milestone"] = df["Milestone"].apply(lambda x: "🏆" if x else "")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Export
        csv_data = progress_to_csv(logs)
        st.download_button(
            "📥 Export Activity Log (CSV)", csv_data,
            file_name="activity_log.csv", mime="text/csv",
        )
    else:
        st.info("No activity logged yet. Start logging above!")

    # ── Skill distribution donut ──────────────────────────────────────────────
    skills = db.get_skills(uid)
    if skills:
        from collections import Counter
        cat_counts = Counter(s.get("category","Other") for s in skills)
        labels = list(cat_counts.keys())
        values = list(cat_counts.values())
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧠 Skill Distribution")
            st.plotly_chart(skill_donut(labels, values), use_container_width=True)
        with col2:
            st.markdown("### 📊 Current Skills")
            sorted_skills = sorted(skills, key=lambda s: -s.get("proficiency_level",0))
            for s in sorted_skills[:10]:
                lvl = s.get("proficiency_level",0)
                bar_w = lvl * 20
                color = S if lvl >= 4 else (P if lvl >= 2 else MT)
                st.markdown(f"""
                <div style="margin-bottom:0.5rem">
                    <div style="display:flex;justify-content:space-between">
                        <span style="font-size:0.85rem">{s.get('skill_name','')}</span>
                        <span style="color:{color};font-size:0.8rem">{lvl}/5</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:100px;height:6px">
                        <div style="background:{color};width:{bar_w}%;
                        height:100%;border-radius:100px"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
