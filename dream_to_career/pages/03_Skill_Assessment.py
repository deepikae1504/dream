import streamlit as st
st.set_page_config(page_title="Skill Assessment | Dream-to-Career AI", page_icon="🧩", layout="wide")
import os, json
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, metric_card, score_gauge, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from agents.skill_gap import SkillGapAgent
from config.constants import SKILL_CATEGORIES
from tools.assessment_tools import calculate_local_readiness, radar_data_from_ratings
from utils.charts import radar_chart

init_db(); init_session(); apply_styles()

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
    if st.session_state.get("api_key"): st.success("✅ Key Active")
    else: st.warning("⚠️ No key set")
    st.markdown("---")
    _models=["gemini-2.0-flash-lite","gemini-2.0-flash","gemini-1.5-pro-latest"]
    _cur=st.session_state.get("gemini_model","gemini-2.0-flash-lite")
    if _cur not in _models: _cur="gemini-2.0-flash-lite"
    _ch=st.selectbox("Model",_models,index=_models.index(_cur),label_visibility="collapsed",key="sb_model")
    if _ch!=_cur: st.session_state.gemini_model=_ch; st.rerun()
    st.markdown("---")
    for _p,_l in [("pages/01_Home.py","🏠 Home"),("pages/02_Career_Analysis.py","🔭 Career Analysis"),("pages/03_Skill_Assessment.py","🧩 Skill Assessment"),("pages/04_Roadmap_Generator.py","🗺️ Roadmap"),("pages/05_Learning_Hub.py","📚 Learning Hub"),("pages/06_AI_Career_Twin.py","🤖 Career Twin"),("pages/07_WhatIf_Simulator.py","⚡ What-If"),("pages/08_Mock_Interview.py","🎤 Interview"),("pages/09_Progress_Dashboard.py","📈 Dashboard"),("pages/10_Analytics.py","🔬 Analytics")]:
        if st.button(_l, key=f"nav_{_l}", use_container_width=True): st.switch_page(_p)

if not st.session_state.get("user_id"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

uid  = st.session_state.user_id
user = db.get_user(uid) or {}
goal = db.get_active_goal(uid) or {}
existing_skills = db.get_skills(uid) or []

page_header("Skill Assessment", "Identify exactly where you are and what you need", "Skill Gap Agent")

if "skill_ratings" not in st.session_state:
    st.session_state.skill_ratings = {s["skill_name"]: s["proficiency_level"] for s in existing_skills}

st.markdown("### Step 1: Rate Your Current Skills (0 = Don't know, 5 = Expert)")
tabs = st.tabs(list(SKILL_CATEGORIES.keys()))
for tab, (category, skills) in zip(tabs, SKILL_CATEGORIES.items()):
    with tab:
        cols = st.columns(2)
        for i, skill in enumerate(skills):
            with cols[i % 2]:
                val = st.slider(skill, 0, 5, st.session_state.skill_ratings.get(skill, 0), key=f"sk_{skill}")
                st.session_state.skill_ratings[skill] = val

custom = st.text_input("Add other skills (comma-separated)", placeholder="e.g. LangChain, FastAPI")

req_skills = []
if goal.get("required_skills"):
    try: req_skills = json.loads(goal["required_skills"])
    except: pass
if req_skills:
    local_score = calculate_local_readiness(st.session_state.skill_ratings, req_skills)
    st.caption(f"⚡ Quick estimate: **{local_score}%** readiness (click Analyze for full AI report)")

col1, col2 = st.columns(2)
with col1:
    if st.button("🧩 Analyze Skill Gaps", use_container_width=True):
        skills_list = [{"name":s,"category":c,"level":l} for c,ss in SKILL_CATEGORIES.items() for s in ss if (l:=st.session_state.skill_ratings.get(s,0))>0]
        if custom:
            for cs in custom.split(","):
                cs=cs.strip()
                if cs: skills_list.append({"name":cs,"category":"Other","level":3})
        db.save_skills(uid, skills_list)
        with st.spinner("Analyzing gaps..."):
            try:
                result = SkillGapAgent().assess_gaps(user.get("dream_career","AI Engineer"), skills_list, req_skills, uid)
                st.session_state["skill_gap"] = result
                st.success("✅ Done!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
with col2:
    if st.button("💾 Save Skills Only", use_container_width=True):
        skills_list=[{"name":s,"category":c,"level":l} for c,ss in SKILL_CATEGORIES.items() for s in ss if (l:=st.session_state.skill_ratings.get(s,0))>0]
        db.save_skills(uid, skills_list)
        st.success("Skills saved!")

gap = st.session_state.get("skill_gap")
if not gap:
    cats, vals = radar_data_from_ratings(st.session_state.skill_ratings)
    if len(cats)>=3: st.plotly_chart(radar_chart(cats, vals, "Your Current Skills"), use_container_width=True)
    st.stop()

if "raw" in gap: st.markdown(gap["raw"]); st.stop()

st.markdown("---")
st.markdown("## 📊 Skill Gap Report")
col1,col2,col3 = st.columns(3)
with col1: st.plotly_chart(score_gauge(gap.get("readiness_score",0), "Readiness"), use_container_width=True)
with col2:
    metric_card("Readiness Level", gap.get("readiness_level","Beginner"), icon="📊")
    metric_card("Est. Timeline", f"{gap.get('estimated_readiness_timeline_months',12)} months", icon="⏱️")
with col3:
    metric_card("Gaps Found", str(len(gap.get("skill_gaps",[]))), icon="🎯")
    metric_card("Strengths", str(len(gap.get("strengths",[]))), icon="💪")

st.info(gap.get("gap_summary",""))

col1,col2 = st.columns(2)
with col1:
    st.markdown("### 💪 Strengths")
    for s in gap.get("strengths",[]):
        name = s.get("skill","") if isinstance(s,dict) else s
        note = s.get("note","") if isinstance(s,dict) else ""
        st.markdown(f"""<div style="background:rgba(0,212,170,0.08);border-radius:8px;padding:0.6rem 1rem;margin:0.3rem 0">
        <strong style="color:{SECONDARY}">✅ {name}</strong><br><small style="color:{TEXT_MUTED}">{note}</small></div>""", unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Wins")
    for qw in gap.get("quick_wins",[]): st.markdown(f"⚡ {qw}")
with col2:
    st.markdown("### 🎯 Skill Gaps")
    pc={"Critical":ACCENT,"High":"#FFB84D","Medium":PRIMARY,"Low":TEXT_MUTED}
    for g in gap.get("skill_gaps",[]):
        skill=g.get("skill","") if isinstance(g,dict) else g
        pri=g.get("priority","Medium") if isinstance(g,dict) else "Medium"
        wks=g.get("effort_weeks",4) if isinstance(g,dict) else 4
        color=pc.get(pri,TEXT_MUTED)
        st.markdown(f"""<div style="border-left:3px solid {color};padding:0.5rem 1rem;margin:0.3rem 0;background:rgba(255,101,132,0.05);border-radius:0 8px 8px 0">
        <div style="display:flex;justify-content:space-between"><strong>{skill}</strong><span style="color:{color};font-size:0.8rem">{pri}</span></div>
        <small style="color:{TEXT_MUTED}">~{wks} weeks</small></div>""", unsafe_allow_html=True)

st.markdown("### 🚀 Start With These")
for s in gap.get("immediate_focus",[]): st.markdown(f"▶️ **{s}**")

cats, vals = radar_data_from_ratings(st.session_state.skill_ratings)
if len(cats)>=3: st.plotly_chart(radar_chart(cats, vals, "Your Skills"), use_container_width=True)

if st.button("▶️ Next: Generate Roadmap", use_container_width=True):
    st.switch_page("pages/04_Roadmap_Generator.py")
