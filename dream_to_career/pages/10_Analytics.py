import streamlit as st
st.set_page_config(page_title="Analytics | Dream-to-Career AI", page_icon="🔬", layout="wide")
import os, json
import pandas as pd
from collections import Counter
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from utils.charts import skill_donut, horizontal_bar
from utils.exporters import profile_snapshot, progress_to_csv
from config.constants import EDUCATION_LEVELS

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

page_header("Analytics & Observability","Agent logs, metrics, and data inspector","System Monitor")
tabs = st.tabs(["📊 Overview","🔍 Agent Logs","📋 Data","💾 Export","⚙️ Settings"])

with tabs[0]:
    logs    = db.get_agent_logs(uid,200) or []
    total   = len(logs)
    success = sum(1 for l in logs if l.get("status")=="success")
    avg_ms  = sum(l.get("execution_time_ms",0) for l in logs)/total if total else 0
    sr      = f"{success/total*100:.0f}%" if total else "0%"

    c1,c2,c3,c4 = st.columns(4)
    for col,(title,val,color) in zip([c1,c2,c3,c4],[
        ("API Calls",  total,           PRIMARY),
        ("Success",    sr,              SECONDARY),
        ("Errors",     total-success,   ACCENT),
        ("Avg ms",     f"{avg_ms:.0f}", PRIMARY),
    ]):
        with col:
            st.markdown(f"""<div style="background:{BG_CARD};border-top:3px solid {color};
            border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:1.5rem;font-weight:700;color:{color}">{val}</div>
            <div style="color:{TEXT_MUTED};font-size:0.75rem">{title}</div></div>""", unsafe_allow_html=True)

    if logs:
        agent_counts = Counter(l.get("agent_name","") for l in logs)
        col1,col2 = st.columns(2)
        with col1:
            st.plotly_chart(skill_donut(list(agent_counts.keys()),list(agent_counts.values()),"Agent Call Distribution"), use_container_width=True)
        with col2:
            agent_times = {}
            for l in logs:
                nm = l.get("agent_name","")
                agent_times.setdefault(nm,[]).append(l.get("execution_time_ms",0))
            avg_t = {k:sum(v)/len(v) for k,v in agent_times.items()}
            sorted_a = sorted(avg_t.items(), key=lambda x:-x[1])
            if sorted_a:
                st.plotly_chart(horizontal_bar([a[0] for a in sorted_a],[a[1] for a in sorted_a],"Avg Response Time (ms)",False), use_container_width=True)
    else:
        st.info("No agent logs yet. Use the app features to generate logs.")

with tabs[1]:
    logs = db.get_agent_logs(uid,100) or []
    if not logs:
        st.info("No agent logs yet.")
    else:
        status_filter = st.selectbox("Filter", ["All","success","error"])
        filtered = [l for l in logs if status_filter=="All" or l.get("status")==status_filter]
        st.markdown(f"Showing **{len(filtered[:30])}** traces")
        for log in filtered[:30]:
            status = log.get("status","")
            color  = SECONDARY if status=="success" else ACCENT
            elapsed= log.get("execution_time_ms",0)
            with st.expander(f"{log.get('agent_name','')} → {log.get('action','')} | {elapsed}ms | {log.get('created_at','')[:16]}"):
                st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                col1,col2 = st.columns(2)
                with col1:
                    st.markdown("**📥 Input**")
                    st.code(str(log.get("input_data",""))[:400], language="text")
                with col2:
                    st.markdown("**📤 Output**")
                    out = str(log.get("output_data",""))[:400]
                    try:
                        st.code(json.dumps(json.loads(out),indent=2)[:400], language="json")
                    except Exception:
                        st.code(out, language="text")
                if log.get("error_message"): st.error(log["error_message"])

with tabs[2]:
    table = st.selectbox("Choose table",["Progress Logs","Skills","Career Goals","Interviews","Health Scores","What-If Simulations"])
    data = []
    if table=="Progress Logs": data = db.get_progress(uid,200) or []
    elif table=="Skills": data = db.get_skills(uid) or []
    elif table=="Career Goals":
        conn=db.get_connection()
        data=[dict(r) for r in conn.execute("SELECT * FROM career_goals WHERE user_id=?",(uid,)).fetchall()]
        conn.close()
    elif table=="Interviews": data = db.get_interviews(uid) or []
    elif table=="Health Scores": data = db.get_health_scores(uid,20) or []
    elif table=="What-If Simulations": data = db.get_whatif_history(uid,20) or []
    if data:
        st.markdown(f"**{len(data)} rows**")
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info(f"No data in {table} yet.")

with tabs[3]:
    skills = db.get_skills(uid) or []
    goal   = db.get_active_goal(uid)
    health = db.get_health_scores(uid,1) or []
    h      = health[0] if health else None
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("**📦 Full Profile (JSON)**")
        st.download_button("⬇️ Download Profile JSON",
            profile_snapshot(user,skills,goal,h),
            file_name="dream_career_profile.json", mime="application/json",
            use_container_width=True)
    with col2:
        st.markdown("**📊 Activity Log (CSV)**")
        st.download_button("⬇️ Download Activity CSV",
            progress_to_csv(db.get_progress(uid,200) or []),
            file_name="activity_log.csv", mime="text/csv",
            use_container_width=True)
    st.markdown("---")
    if st.checkbox("⚠️ Show data reset options"):
        col_a,col_b = st.columns(2)
        with col_a:
            if st.button("🗑️ Clear Activity Logs", use_container_width=True):
                conn=db.get_connection()
                conn.execute("DELETE FROM progress_tracking WHERE user_id=?",(uid,))
                conn.commit(); conn.close()
                st.success("Cleared."); st.rerun()
        with col_b:
            if st.button("🗑️ Clear Agent Logs", use_container_width=True):
                conn=db.get_connection()
                conn.execute("DELETE FROM agent_logs WHERE user_id=?",(uid,))
                conn.commit(); conn.close()
                st.success("Cleared."); st.rerun()

with tabs[4]:
    st.markdown("### ⚙️ Update Your Profile")
    with st.form("profile_form"):
        c1,c2 = st.columns(2)
        with c1:
            name  = st.text_input("Name", value=user.get("name",""))
            role  = st.text_input("Current Role", value=user.get("current_role",""))
            exp   = st.slider("Years of Experience", 0, 20, int(user.get("experience_years",0)))
        with c2:
            dream = st.text_input("Dream Career", value=user.get("dream_career",""))
            cur_edu = user.get("education","Bachelor's Degree")
            edu   = st.selectbox("Education", EDUCATION_LEVELS,
                index=EDUCATION_LEVELS.index(cur_edu) if cur_edu in EDUCATION_LEVELS else 2)
            email = st.text_input("Email", value=user.get("email",""))
        if st.form_submit_button("💾 Update Profile", use_container_width=True):
            db.upsert_user(name, email, role, exp, edu, dream)
            st.session_state.user_name    = name
            st.session_state.dream_career = dream
            st.success("✅ Profile updated!"); st.rerun()
