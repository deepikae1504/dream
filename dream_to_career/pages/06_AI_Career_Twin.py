import streamlit as st
st.set_page_config(page_title="AI Career Twin | Dream-to-Career AI", page_icon="🤖", layout="wide")
import os, json
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, metric_card, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from agents.career_twin import CareerTwinAgent
from agents.recruiter import RecruiterAgent

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

uid        = st.session_state.user_id
user       = db.get_user(uid) or {}
skills     = db.get_skills(uid) or []
progress   = db.get_progress(uid) or []
interviews = db.get_interviews(uid) or []
health_rows= db.get_health_scores(uid,1) or []
health     = health_rows[0] if health_rows else {}

page_header("AI Career Twin","See your predicted future and optimize your path","AI Career Twin")
tab1,tab2 = st.tabs(["🤖 Career Twin","👔 Recruiter View"])

with tab1:
    if st.button("🔮 Generate My Career Twin", use_container_width=True):
        with st.spinner("Creating your AI Career Twin..."):
            try:
                twin = CareerTwinAgent().predict_future(user, skills, progress, health, uid)
                st.session_state["career_twin"] = twin
                db.save_career_twin(uid, str({"skills":len(skills)}),
                    json.dumps(twin.get("career_milestones_predicted",[])),
                    json.dumps(twin.get("critical_risks",[])),
                    json.dumps(twin.get("opportunities",[])),
                    json.dumps(twin.get("missing_skills_for_success",[])),
                    twin.get("success_probability",50),
                    json.dumps(twin.get("career_milestones_predicted",[])))
                st.success("✅ Career Twin created!"); st.rerun()
            except Exception as e: st.error(f"Error: {e}")

    twin = st.session_state.get("career_twin")
    if not twin:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(108,99,255,0.15),rgba(0,212,170,0.1));
        border:1px solid rgba(108,99,255,0.3);border-radius:20px;padding:2rem;text-align:center;margin:2rem 0">
        <div style="font-size:3rem">🤖</div>
        <h3>Meet Your AI Career Twin</h3>
        <p style="color:{TEXT_MUTED};max-width:400px;margin:0 auto">
        Your Career Twin simulates your future trajectory, predicts outcomes, identifies risks,
        and tells you exactly what to do to reach your dream career.</p></div>""", unsafe_allow_html=True)
        st.stop()

    if "raw" in twin: st.markdown(twin["raw"]); st.stop()

    prob = twin.get("success_probability",50)
    pc   = SECONDARY if prob>=70 else (PRIMARY if prob>=50 else ACCENT)
    st.markdown(f"""<div style="background:{BG_CARD};border:2px solid {pc}40;border-radius:20px;padding:2rem;margin:1rem 0">
    <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap">
        <div style="font-size:3rem">🤖</div>
        <div style="flex:1">
            <h2 style="margin:0;color:{pc}">{twin.get('twin_name','Future You')}</h2>
            <p style="color:{TEXT_MUTED};margin:0.3rem 0">{twin.get('current_trajectory','')}</p>
        </div>
        <div style="text-align:center">
            <div style="font-size:3rem;font-weight:700;color:{pc}">{prob}%</div>
            <div style="color:{TEXT_MUTED};font-size:0.85rem">Success Probability</div>
        </div>
    </div>
    <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.05)">
        <em style="color:{SECONDARY}">&ldquo;{twin.get('twin_message','')}&rdquo;</em>
    </div></div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: metric_card("Timeline", twin.get("predicted_timeline",""), icon="⏱️")
    with c2: metric_card("First Salary", twin.get("predicted_first_salary",""), icon="💰")
    with c3: metric_card("3-Year Salary", twin.get("predicted_3_year_salary",""), icon="📈")

    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### ⚠️ Critical Risks")
        for r in twin.get("critical_risks",[]):
            if isinstance(r,dict):
                rc = {"High":ACCENT,"Medium":"#FFB84D","Low":TEXT_MUTED}.get(r.get("probability","Medium"),TEXT_MUTED)
                st.markdown(f"""<div style="background:rgba(255,101,132,0.08);border-left:3px solid {rc};
                border-radius:0 8px 8px 0;padding:0.8rem;margin:0.3rem 0">
                <strong>⚠️ {r.get('risk','')}</strong>
                <br><small style="color:{SECONDARY}">🛡️ {r.get('mitigation','')}</small></div>""",
                unsafe_allow_html=True)
    with col2:
        st.markdown("### 🌟 Opportunities")
        for o in twin.get("opportunities",[]):
            if isinstance(o,dict):
                st.markdown(f"""<div style="background:rgba(0,212,170,0.08);border-left:3px solid {SECONDARY};
                border-radius:0 8px 8px 0;padding:0.8rem;margin:0.3rem 0">
                <strong>🎯 {o.get('opportunity','')}</strong>
                <br><small style="color:{SECONDARY}">→ {o.get('action_needed','')}</small></div>""",
                unsafe_allow_html=True)

    missing = twin.get("missing_skills_for_success",[])
    if missing:
        st.markdown("### 🎯 Missing Skills for Success")
        st.markdown(" ".join([
            f'<span style="background:rgba(255,101,132,0.1);border:1px solid rgba(255,101,132,0.3);'
            f'border-radius:20px;padding:0.2rem 0.7rem;margin:0.2rem;display:inline-block;color:{ACCENT}">{s}</span>'
            for s in missing]), unsafe_allow_html=True)

with tab2:
    if st.button("👔 Get Recruiter Evaluation", use_container_width=True):
        with st.spinner("Evaluating your profile as a recruiter..."):
            try:
                ev = RecruiterAgent().evaluate_profile(user, skills, interviews, uid)
                st.session_state["recruiter_eval"] = ev
                st.success("✅ Done!"); st.rerun()
            except Exception as e: st.error(f"Error: {e}")

    ev = st.session_state.get("recruiter_eval")
    if not ev:
        st.info("Click the button above to see how a real recruiter views your profile."); st.stop()
    if "raw" in ev: st.markdown(ev["raw"]); st.stop()

    prob = ev.get("hiring_probability",30)
    pc   = SECONDARY if prob>=60 else (PRIMARY if prob>=40 else ACCENT)
    st.markdown(f"""<div style="background:{BG_CARD};border:2px solid {pc}40;border-radius:16px;padding:1.5rem;margin:1rem 0">
    <h3 style="margin:0">👔 First Impression</h3>
    <p style="color:{TEXT_MUTED}">{ev.get('first_impression','')}</p>
    <div style="display:flex;gap:2rem;flex-wrap:wrap;margin-top:1rem">
        <div><div style="font-size:2.5rem;font-weight:700;color:{pc}">{prob}%</div>
        <div style="color:{TEXT_MUTED};font-size:0.8rem">Hire Probability</div></div>
        <div><div style="font-size:2.5rem;font-weight:700;color:{PRIMARY}">{ev.get('profile_grade','C')}</div>
        <div style="color:{TEXT_MUTED};font-size:0.8rem">Profile Grade</div></div>
    </div></div>""", unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### 💪 Recruiter Sees")
        for s in ev.get("strengths_as_recruiter_sees",[]): st.markdown(f"✅ {s}")
        st.markdown("### 📄 Resume Tips")
        for t in ev.get("resume_advice",[]): st.markdown(f"💡 {t}")
    with col2:
        st.markdown("### 🚩 Red Flags")
        for r in ev.get("red_flags",[]): st.markdown(f"🚩 {r}")
        st.markdown("### 🎯 Top Action Right Now")
        st.info(ev.get("top_action",""))
    st.markdown(f"""<div style="background:rgba(108,99,255,0.08);border-left:4px solid {PRIMARY};
    border-radius:0 12px 12px 0;padding:1rem 1.5rem;margin-top:1rem">
    <strong>Recruiter's Verdict:</strong><br>{ev.get('recruiter_verdict','')}</div>""",
    unsafe_allow_html=True)
