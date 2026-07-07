"""
pages/10_🔬_Analytics.py
Analytics & Admin — agent execution logs, observability traces,
system performance, and raw data export.
"""
import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter

from database import db
from utils.session import init_session, login_gate
from utils.ui_components import apply_styles, page_header
from utils.charts import progress_line, horizontal_bar, skill_donut
from utils.exporters import profile_snapshot
from config.constants import COLORS, AGENT_NAMES

P  = COLORS["primary"]
S  = COLORS["secondary"]
A  = COLORS["accent"]
W  = COLORS["warning"]
MT = COLORS["text_muted"]
BC = COLORS["bg_card"]

# ── Status badge helper ───────────────────────────────────────────────────────

def _status_badge(status: str) -> str:
    color = S if status == "success" else A
    icon  = "✅" if status == "success" else "❌"
    return (
        f'<span style="background:{color}20;color:{color};border:1px solid {color}40;'
        f'border-radius:20px;padding:0.1rem 0.6rem;font-size:0.75rem">{icon} {status}</span>'
    )


def render():
    init_session()
    apply_styles()
    page_header(
        "Analytics & Observability",
        "Agent execution traces, system metrics, and raw data inspector",
        "System Monitor",
    )

    if not login_gate("Analytics"):
        return

    uid  = st.session_state.user_id
    user = db.get_user(uid)

    # ── Tab layout ────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Overview",
        "🔍 Agent Traces",
        "📋 Raw Data",
        "💾 Export",
        "⚙️ Settings",
    ])

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1 — Overview
    # ═══════════════════════════════════════════════════════════════════════════
    with tabs[0]:
        st.markdown("### 📊 System Overview")

        logs      = db.get_agent_logs(uid, 200)
        progress  = db.get_progress(uid, 60)
        interviews= db.get_interviews(uid)
        skills    = db.get_skills(uid)
        health    = db.get_health_scores(uid, 10)
        goal      = db.get_active_goal(uid)

        # Top KPIs
        total_calls   = len(logs)
        success_calls = sum(1 for l in logs if l.get("status") == "success")
        error_calls   = total_calls - success_calls
        avg_ms = (
            sum(l.get("execution_time_ms", 0) for l in logs) / total_calls
            if total_calls else 0
        )
        success_rate = (success_calls / total_calls * 100) if total_calls else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        for col, title, value, icon, color in [
            (c1, "Total API Calls",  total_calls,          "🤖", P),
            (c2, "Success Rate",     f"{success_rate:.1f}%","✅", S),
            (c3, "Errors",           error_calls,           "❌", A),
            (c4, "Avg Response",     f"{avg_ms:.0f} ms",   "⚡", W),
            (c5, "Skills Tracked",   len(skills),           "🧠", P),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:{BC};border:1px solid {color}30;
                border-radius:12px;padding:1rem;text-align:center;border-top:3px solid {color}">
                    <div style="font-size:1.2rem">{icon}</div>
                    <div style="font-size:1.5rem;font-weight:700;color:{color}">{value}</div>
                    <div style="color:{MT};font-size:0.75rem">{title}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Agent call distribution
        col1, col2 = st.columns(2)
        with col1:
            if logs:
                agent_counts = Counter(l.get("agent_name","Unknown") for l in logs)
                names  = list(agent_counts.keys())
                values = list(agent_counts.values())
                st.plotly_chart(
                    skill_donut(names, values, "Agent Call Distribution"),
                    use_container_width=True,
                )
            else:
                st.info("No agent logs yet. Run some analyses to see metrics.")

        with col2:
            if logs:
                # Response time by agent
                agent_times: dict = {}
                for l in logs:
                    name = l.get("agent_name","Unknown")
                    ms   = l.get("execution_time_ms", 0)
                    agent_times.setdefault(name, []).append(ms)
                avg_times = {k: sum(v)/len(v) for k, v in agent_times.items()}
                sorted_agents = sorted(avg_times.items(), key=lambda x: -x[1])
                st.plotly_chart(
                    horizontal_bar(
                        [a[0] for a in sorted_agents],
                        [a[1] for a in sorted_agents],
                        title="Avg Response Time (ms)",
                        color_scale=False,
                    ),
                    use_container_width=True,
                )

        # Career goal status
        if goal:
            st.markdown("### 🎯 Active Career Goal")
            st.markdown(f"""
            <div style="background:{BC};border:1px solid rgba(108,99,255,0.2);
            border-radius:14px;padding:1.2rem 1.5rem">
                <div style="font-size:1.1rem;font-weight:600">
                    🚀 {goal.get('target_career','')}
                </div>
                <div style="color:{MT};font-size:0.85rem;margin-top:0.5rem">
                    Created: {goal.get('created_at','')[:10]} &nbsp;·&nbsp;
                    Timeline: {goal.get('target_timeline_months',12)} months &nbsp;·&nbsp;
                    Status: <span style="color:{S}">{goal.get('status','active')}</span>
                </div>
                <div style="margin-top:0.5rem;color:{MT};font-size:0.85rem">
                    Market demand: {goal.get('market_demand','')}
                </div>
            </div>""", unsafe_allow_html=True)

        # Interview performance trend
        if interviews:
            st.markdown("### 🎤 Interview Performance")
            scores = [i.get("overall_score",0) for i in reversed(interviews)]
            dates  = [i.get("created_at","")[:10] for i in reversed(interviews)]
            st.plotly_chart(
                progress_line(dates, scores, "Score", "Interview Scores Over Time", 220),
                use_container_width=True,
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2 — Agent Traces
    # ═══════════════════════════════════════════════════════════════════════════
    with tabs[1]:
        st.markdown("### 🔍 Agent Execution Traces")

        logs = db.get_agent_logs(uid, 100)
        if not logs:
            st.info("No agent logs yet. Run analyses across pages to populate traces.")
        else:
            # Filter bar
            col1, col2, col3 = st.columns(3)
            with col1:
                agent_filter = st.selectbox(
                    "Filter by Agent",
                    ["All"] + sorted({l.get("agent_name","") for l in logs}),
                )
            with col2:
                status_filter = st.selectbox("Filter by Status", ["All","success","error"])
            with col3:
                limit = st.slider("Show last N", 10, 100, 30, 10)

            filtered = [
                l for l in logs
                if (agent_filter == "All" or l.get("agent_name") == agent_filter)
                and (status_filter == "All" or l.get("status") == status_filter)
            ][:limit]

            st.markdown(f"Showing **{len(filtered)}** traces")

            for log in filtered:
                status  = log.get("status","unknown")
                elapsed = log.get("execution_time_ms",0)
                agent   = log.get("agent_name","")
                action  = log.get("action","")
                ts      = log.get("created_at","")[:16]

                badge = _status_badge(status)
                speed_color = S if elapsed < 3000 else (W if elapsed < 8000 else A)

                with st.expander(
                    f"{agent}  ›  {action}  —  {ts}",
                    expanded=False
                ):
                    st.markdown(
                        f'{badge} &nbsp; '
                        f'<span style="color:{speed_color}">⚡ {elapsed} ms</span>',
                        unsafe_allow_html=True,
                    )

                    col_in, col_out = st.columns(2)
                    with col_in:
                        st.markdown("**📥 Input (truncated)**")
                        raw_in = log.get("input_data","")
                        st.code(raw_in[:600] if raw_in else "—", language="text")
                    with col_out:
                        st.markdown("**📤 Output (truncated)**")
                        raw_out = log.get("output_data","")
                        # Pretty-print if JSON
                        try:
                            parsed = json.loads(raw_out[:600])
                            st.code(json.dumps(parsed, indent=2)[:600], language="json")
                        except Exception:
                            st.code(raw_out[:600] if raw_out else "—", language="text")

                    if log.get("error_message"):
                        st.error(f"Error: {log['error_message']}")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3 — Raw Data Inspector
    # ═══════════════════════════════════════════════════════════════════════════
    with tabs[2]:
        st.markdown("### 📋 Raw Data Inspector")

        table = st.selectbox("Choose table", [
            "Progress Logs",
            "Skills",
            "Career Goals",
            "Interviews",
            "Health Scores",
            "What-If Simulations",
            "Career Twin Predictions",
            "Agent Logs",
        ])

        data: list = []
        if table == "Progress Logs":
            data = db.get_progress(uid, 200)
        elif table == "Skills":
            data = db.get_skills(uid)
        elif table == "Career Goals":
            conn = db.get_connection()
            rows = conn.execute("SELECT * FROM career_goals WHERE user_id=?", (uid,)).fetchall()
            conn.close()
            data = [dict(r) for r in rows]
        elif table == "Interviews":
            data = db.get_interviews(uid)
        elif table == "Health Scores":
            data = db.get_health_scores(uid, 20)
        elif table == "What-If Simulations":
            data = db.get_whatif_history(uid, 20)
        elif table == "Career Twin Predictions":
            conn = db.get_connection()
            rows = conn.execute(
                "SELECT * FROM career_twin_predictions WHERE user_id=?", (uid,)).fetchall()
            conn.close()
            data = [dict(r) for r in rows]
        elif table == "Agent Logs":
            data = db.get_agent_logs(uid, 100)

        if data:
            df = pd.DataFrame(data)
            st.markdown(f"**{len(df)} rows** in `{table}`")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No data found in `{table}` for your account.")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 4 — Export
    # ═══════════════════════════════════════════════════════════════════════════
    with tabs[3]:
        st.markdown("### 💾 Export Your Data")

        skills  = db.get_skills(uid)
        goal    = db.get_active_goal(uid)
        health  = db.get_health_scores(uid, 1)
        h       = health[0] if health else None

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📦 Full Profile Snapshot (JSON)**")
            st.markdown(
                "Everything in one file: profile, skills, active goal, health score."
            )
            snapshot = profile_snapshot(user, skills, goal, h)
            st.download_button(
                "⬇️ Download Profile JSON",
                data=snapshot,
                file_name=f"dream_career_profile_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
            )

        with col2:
            st.markdown("**📊 Activity Log (CSV)**")
            st.markdown("All your logged study sessions as a spreadsheet.")
            from utils.exporters import progress_to_csv
            logs_data = db.get_progress(uid, 200)
            csv_data  = progress_to_csv(logs_data)
            st.download_button(
                "⬇️ Download Activity CSV",
                data=csv_data,
                file_name=f"activity_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown("**⚠️ Danger Zone**")
        if st.checkbox("Show data reset options"):
            st.warning(
                "These actions permanently delete data and cannot be undone."
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🗑️ Clear Activity Logs", use_container_width=True):
                    conn = db.get_connection()
                    conn.execute("DELETE FROM progress_tracking WHERE user_id=?", (uid,))
                    conn.commit(); conn.close()
                    st.success("Activity logs cleared.")
            with col_b:
                if st.button("🗑️ Clear Agent Logs", use_container_width=True):
                    conn = db.get_connection()
                    conn.execute("DELETE FROM agent_logs WHERE user_id=?", (uid,))
                    conn.commit(); conn.close()
                    st.success("Agent logs cleared.")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 5 — Settings
    # ═══════════════════════════════════════════════════════════════════════════
    with tabs[4]:
        st.markdown("### ⚙️ Account Settings")

        current = db.get_user(uid)

        with st.form("update_profile"):
            col1, col2 = st.columns(2)
            with col1:
                name  = st.text_input("Name", value=current.get("name",""))
                role  = st.text_input("Current Role", value=current.get("current_role",""))
                exp   = st.slider("Years of Experience", 0, 20,
                                  int(current.get("experience_years", 0)))
            with col2:
                dream = st.text_input("Dream Career", value=current.get("dream_career",""))
                from config.constants import EDUCATION_LEVELS
                edu_options = EDUCATION_LEVELS
                current_edu = current.get("education","Bachelor's Degree")
                edu_idx = (edu_options.index(current_edu)
                           if current_edu in edu_options else 2)
                edu = st.selectbox("Education", edu_options, index=edu_idx)
                email = st.text_input("Email", value=current.get("email",""))

            if st.form_submit_button("💾 Update Profile", use_container_width=True):
                db.upsert_user(name, email, role, exp, edu, dream)
                st.session_state.user_name   = name
                st.session_state.dream_career = dream
                st.success("✅ Profile updated successfully!")
                st.rerun()

        st.markdown("---")
        st.markdown("### 🔑 API Key")
        current_key = st.session_state.get("api_key","")
        new_key = st.text_input(
            "Gemini API Key",
            value=current_key,
            type="password",
            help="Get your key at https://aistudio.google.com/app/apikey",
        )
        if st.button("💾 Save API Key"):
            st.session_state.api_key = new_key.strip()
            st.success("✅ API key saved for this session.")

        st.markdown("---")
        st.markdown("### 🔍 Observability Preferences")
        show_traces = st.toggle(
            "Show agent trace expanders on all pages",
            value=st.session_state.get("show_observability", False),
        )
        st.session_state.show_observability = show_traces
        if show_traces:
            st.info(
                "Agent trace expanders will appear at the bottom of "
                "Career Analysis, Skill Assessment, and other pages."
            )
