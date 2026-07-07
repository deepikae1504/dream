import streamlit as st
st.set_page_config(page_title="Career Analysis | Dream-to-Career AI", page_icon="🔭", layout="wide")

import os, json
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, metric_card, skill_chips, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from agents.career_analyst import CareerAnalystAgent

init_db(); init_session(); apply_styles()

# SIDEBAR
with st.sidebar:
    st.markdown("### 🔑 API Key")
    if not st.session_state.get("api_key"):
        _e = os.environ.get("GEMINI_API_KEY","")
        if _e: st.session_state.api_key = _e
    _t = st.text_input("Key", value=st.session_state.get("api_key",""), type="password", placeholder="Paste API key...", label_visibility="collapsed", key="sb_key")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("✅ Save", key="sb_save", use_container_width=True):
            if _t and len(_t.strip())>5: st.session_state.api_key=_t.strip(); st.rerun()
            else: st.error("Paste key first")
    with c2:
        if st.button("🗑️ Clear", key="sb_clr", use_container_width=True):
            st.session_state.api_key=""; st.rerun()
    if st.session_state.get("api_key"): st.success(f"✅ Active")
    else: st.warning("⚠️ No key")
    st.markdown("---")
    st.markdown("### 🤖 Model")
    _models=["gemini-2.0-flash-lite","gemini-2.0-flash","gemini-1.5-pro-latest"]
    _cur=st.session_state.get("gemini_model","gemini-2.0-flash-lite")
    if _cur not in _models: _cur="gemini-2.0-flash-lite"
    _ch=st.selectbox("Model",_models,index=_models.index(_cur),label_visibility="collapsed",key="sb_model")
    if _ch!=_cur: st.session_state.gemini_model=_ch; st.rerun()
    st.markdown("---")
    for _p,_l in [("pages/01_Home.py","🏠 Home"),("pages/02_Career_Analysis.py","🔭 Career Analysis"),("pages/03_Skill_Assessment.py","🧩 Skill Assessment"),("pages/04_Roadmap_Generator.py","🗺️ Roadmap"),("pages/05_Learning_Hub.py","📚 Learning Hub"),("pages/06_AI_Career_Twin.py","🤖 Career Twin"),("pages/07_WhatIf_Simulator.py","⚡ What-If"),("pages/08_Mock_Interview.py","🎤 Interview"),("pages/09_Progress_Dashboard.py","📈 Dashboard"),("pages/10_Analytics.py","🔬 Analytics")]:
        if st.button(_l, key=f"nav_{_l}", use_container_width=True): st.switch_page(_p)

# GUARD
if not st.session_state.get("user_id"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

uid  = st.session_state.user_id
user = db.get_user(uid) or {}

page_header("Career Analysis", "Deep market intelligence for your target role", "Career Analyst Agent")

career_input = st.text_input("Target Career Role", value=user.get("dream_career",""), placeholder="e.g. Machine Learning Engineer")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔭 Analyze This Career", use_container_width=True):
        if career_input:
            with st.spinner("Analyzing career..."):
                try:
                    result = CareerAnalystAgent().analyze(career_input, user, uid)
                    st.session_state["career_analysis"] = result
                    goal_id = db.save_career_goal(uid, career_input,
                        career_report=json.dumps(result),
                        required_skills=json.dumps(result.get("required_skills",[])),
                        market_demand=result.get("market_demand",""))
                    st.session_state["active_goal_id"] = goal_id
                    st.success("✅ Done!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
with col2:
    goal = db.get_active_goal(uid) or {}
    if goal.get("career_report"):
        if st.button("📂 Load Previous", use_container_width=True):
            st.session_state["career_analysis"] = json.loads(goal["career_report"])
            st.rerun()

analysis = st.session_state.get("career_analysis")
if not analysis:
    st.info("Enter a career above and click Analyze.")
    st.stop()

if "raw" in analysis:
    st.markdown(analysis["raw"])
    st.stop()

st.markdown(f"## {analysis.get('career_title', career_input)}")
col1,col2,col3,col4 = st.columns(4)
with col1: metric_card("Market Demand", analysis.get("market_demand","N/A").split()[0], icon="📈")
with col2: metric_card("Avg. Salary", analysis.get("avg_salary_range","₹--"), icon="💰")
with col3: metric_card("Skills Required", str(len(analysis.get("required_skills",[]))), icon="🧠")
with col4: metric_card("Top Companies", str(len(analysis.get("top_companies",[]))), icon="🏢")

st.markdown(f"""<div style="background:rgba(108,99,255,0.08);border-left:4px solid {PRIMARY};border-radius:0 12px 12px 0;padding:1rem 1.5rem;margin:1rem 0">
<p style="margin:0">{analysis.get('overview','')}</p></div>""", unsafe_allow_html=True)

st.markdown("### 🧠 Required Skills")
all_skills = analysis.get("required_skills",[])
skill_chips(all_skills)

stages = analysis.get("career_stages",[])
if stages:
    st.markdown("### 🪜 Career Progression")
    cols = st.columns(len(stages))
    for i,(col,stage) in enumerate(zip(cols,stages)):
        with col:
            color=[PRIMARY,SECONDARY,ACCENT,"#FFB84D"][i%4]
            st.markdown(f"""<div style="background:{BG_CARD};border-top:3px solid {color};border-radius:12px;padding:1rem;text-align:center">
            <div style="font-weight:700;color:{color}">{stage.get('stage','')}</div>
            <div style="color:{TEXT_MUTED};font-size:0.8rem">{stage.get('timeline','')}</div>
            <div style="font-size:0.85rem">{stage.get('salary','')}</div></div>""", unsafe_allow_html=True)

companies = analysis.get("top_companies",[])
if companies:
    st.markdown("### 🏢 Top Companies")
    st.markdown(" ".join([f'<span style="background:rgba(0,212,170,0.1);border:1px solid rgba(0,212,170,0.3);border-radius:20px;padding:0.3rem 0.8rem;margin:0.2rem;display:inline-block">{c}</span>' for c in companies]), unsafe_allow_html=True)

col1,col2 = st.columns(2)
with col1:
    st.markdown("### 🌱 Growth Outlook")
    st.info(analysis.get("growth_outlook",""))
    st.markdown("### ✅ Success Factors")
    for f in analysis.get("success_factors",[]): st.markdown(f"✅ {f}")
with col2:
    st.markdown("### ⚠️ Challenges")
    for c in analysis.get("challenges",[]): st.markdown(f"⚠️ {c}")
    st.markdown("### 🎖️ Key Certifications")
    for cert in analysis.get("key_certifications",[]): st.markdown(f"• {cert}")

st.markdown("### 🗓️ A Typical Day")
st.info(analysis.get("daily_work",""))

if st.button("▶️ Next: Assess My Skills", use_container_width=True):
    st.switch_page("pages/03_Skill_Assessment.py")
