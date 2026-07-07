import streamlit as st
st.set_page_config(page_title="Dashboard | Dream-to-Career AI", page_icon="📈", layout="wide")
import os, json
from collections import defaultdict
import pandas as pd
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, health_score_bars, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from agents.accountability import AccountabilityAgent
from tools.career_tools import build_progress_summary
from config.constants import ACTIVITY_TYPES
from utils.charts import score_gauge, health_history_chart, progress_line, skill_donut
from utils.exporters import progress_to_csv

init_db(); init_session(); apply_styles()

with st.sidebar:
    st.markdown("### 🔑 API Key")
    if not st.session_state.get("api_key"):
        _e = os.environ.get("GEMINI_API_KEY","")
        if _e: st.session_state.api_key = _e
    _t = st.text_input("Key", value=st.session_state.get("api_key",""), type="password",
        placeholder="Paste API key...", label_visibility="collapsed", key="sb_key")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("✅ Save", key="sb_save", use_container_width=True):
            if _t and len(_t.strip())>5: st.session_state.api_key=_t.strip(); st.rerun()
            else: st.error("Paste key first")
    with c2:
        if st.button("🗑️ Clear", key="sb_clr", use_container_width=True):
            st.session_state.api_key=""; st.rerun()
    if st.session_state.get("api_key"): st.success("✅ Key Active")
    else: st.warning("⚠️ No key set")
    st.markdown("---")
    _models = ["gemini-2.0-flash-lite","gemini-2.0-flash","gemini-1.5-pro-latest"]
    _cur = st.session_state.get("gemini_model","gemini-2.0-flash-lite")
    if _cur not in _models: _cur = "gemini-2.0-flash-lite"
    _ch = st.selectbox("Model", _models, index=_models.index(_cur), label_visibility="collapsed", key="sb_model")
    if _ch != _cur: st.session_state.gemini_model=_ch; st.rerun()
    st.markdown("---")
    for _p,_l in [("pages/01_Home.py","🏠 Home"),("pages/02_Career_Analysis.py","🔭 Career Analysis"),
        ("pages/03_Skill_Assessment.py","🧩 Skill Assessment"),("pages/04_Roadmap_Generator.py","🗺️ Roadmap"),
        ("pages/05_Learning_Hub.py","📚 Learning Hub"),("pages/06_AI_Career_Twin.py","🤖 Career Twin"),
        ("pages/07_WhatIf_Simulator.py","⚡ What-If"),("pages/08_Mock_Interview.py","🎤 Interview"),
        ("pages/09_Progress_Dashboard.py","📈 Dashboard"),("pages/10_Analytics.py","🔬 Analytics")]:
        if st.button(_l, key=f"nav_{_l}", use_container_width=True): st.switch_page(_p)

if not st.session_state.get("user_id"):
    st.warning("Please complete onboarding on the Home page first."); st.stop()

uid  = st.session_state.user_id
user = db.get_user(uid) or {}

page_header("Progress Dashboard","Your weekly career health score and activity log","Accountability Agent")

summary = build_progress_summary(uid)
cols = st.columns(5)
for col,title,val,icon in zip(cols,[
    ("Hours (30d)", summary["total_hours_30d"],    "⏱️"),
    ("Active Days", summary["active_days_30d"],    "📅"),
    ("Streak",      f"{summary['streak']} days",   "🔥"),
    ("Milestones",  summary["milestones_30d"],     "🏆"),
    ("Interview",   f"{summary['avg_interview']}/10","🎤"),
]):
    title_s,val_s,icon_s = title
    with col:
        st.markdown(f"""<div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
        border-radius:12px;padding:1rem;text-align:center">
        <div style="font-size:1.2rem">{icon_s}</div>
        <div style="font-size:1.5rem;font-weight:700;color:{SECONDARY}">{val_s}</div>
        <div style="color:{TEXT_MUTED};font-size:0.72rem">{title_s}</div></div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📊 Career Health Score")

health_rows = db.get_health_scores(uid,10) or []
current     = health_rows[0] if health_rows else {}
col1,col2,col3 = st.columns([1,2,1])

with col1:
    overall = current.get("overall_score",0) if current else 0
    st.plotly_chart(score_gauge(overall,"Health Score"), use_container_width=True)

with col2:
    if current:
        health_score_bars(current)
        msg   = current.get("motivational_message","")
        focus = current.get("this_week_focus","")
        if msg:
            st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(108,99,255,0.1),rgba(0,212,170,0.06));
            border:1px solid rgba(108,99,255,0.25);border-radius:14px;padding:1rem;margin-top:0.5rem">
            <em style="color:{SECONDARY}">&ldquo;{msg}&rdquo;</em>
            {f'<br><strong>🎯 This week: {focus}</strong>' if focus else ''}</div>""", unsafe_allow_html=True)
    else:
        st.info("No health score yet. Click **Generate** →")

with col3:
    if st.button("🔄 Generate\nHealth Score", use_container_width=True):
        with st.spinner("Calculating..."):
            try:
                logs   = db.get_progress(uid,30) or []
                ivs    = db.get_interviews(uid,10) or []
                iscores= [i.get("overall_score",0) for i in ivs]
                result = AccountabilityAgent().calculate_health_score(logs, iscores, user, uid)
                st.session_state["health_score"] = result
                db.save_health_score(uid,
                    result.get("learning_consistency",0),
                    result.get("skill_development",0),
                    result.get("project_building",0),
                    result.get("interview_readiness",0),
                    result.get("overall_score",0),
                    json.dumps(result.get("insights",[])))
                st.success("✅ Done!"); st.rerun()
            except Exception as e: st.error(f"Error: {e}")

if len(health_rows) >= 2:
    st.plotly_chart(health_history_chart(health_rows), use_container_width=True)

st.markdown("---")
st.markdown("### ✏️ Log Today's Activity")
with st.form("log_form"):
    c1,c2 = st.columns(2)
    with c1:
        activity = st.selectbox("Activity", ACTIVITY_TYPES)
        hours    = st.number_input("Hours", 0.0, 16.0, 1.0, 0.5)
    with c2:
        desc      = st.text_area("What did you do?", height=90, placeholder="Describe your study session...")
        milestone = st.checkbox("Completed a milestone 🏆")
    if st.form_submit_button("💾 Save", use_container_width=True):
        if desc.strip() and hours > 0:
            db.log_progress(uid, activity, desc, hours, milestone)
            st.success("✅ Activity logged!"); st.rerun()
        else:
            st.error("Please fill in description and hours > 0.")

st.markdown("### 📋 Activity History")
logs = db.get_progress(uid, 30) or []
if logs:
    daily = defaultdict(float)
    for l in logs: daily[l.get("date","")]+=float(l.get("hours_spent",0))
    sd = sorted(daily.items())
    if len(sd) >= 2:
        st.plotly_chart(progress_line([d[0] for d in sd],[d[1] for d in sd],
            "Hours","Daily Study Hours",220), use_container_width=True)
    df = pd.DataFrame(logs)[["date","activity_type","description","hours_spent","milestone_completed"]]
    df.columns = ["Date","Activity","Description","Hours","Milestone"]
    df["Milestone"] = df["Milestone"].apply(lambda x: "🏆" if x else "")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("📥 Export CSV", progress_to_csv(logs), file_name="activity.csv", mime="text/csv")
else:
    st.info("No activity logged yet. Start logging above!")

skills = db.get_skills(uid) or []
if skills:
    from collections import Counter
    cat_counts = Counter(s.get("category","Other") for s in skills)
    st.markdown("### 🧠 Skill Distribution")
    st.plotly_chart(skill_donut(list(cat_counts.keys()),list(cat_counts.values())), use_container_width=True)
