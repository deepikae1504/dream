import streamlit as st
st.set_page_config(page_title="Roadmap | Dream-to-Career AI", page_icon="🗺️", layout="wide")
import os, json
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, progress_timeline, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from agents.roadmap_planner import RoadmapPlannerAgent
from utils.exporters import roadmap_to_markdown

init_db(); init_session(); apply_styles()

with st.sidebar:
    st.markdown("### 🔑 API Key")
    if not st.session_state.get("api_key"):
        _e=os.environ.get("GEMINI_API_KEY","")
        if _e: st.session_state.api_key=_e
    _t=st.text_input("Key",value=st.session_state.get("api_key",""),type="password",placeholder="Paste API key...",label_visibility="collapsed",key="sb_key")
    c1,c2=st.columns(2)
    with c1:
        if st.button("✅ Save",key="sb_save",use_container_width=True):
            if _t and len(_t.strip())>5: st.session_state.api_key=_t.strip(); st.rerun()
            else: st.error("Paste key first")
    with c2:
        if st.button("🗑️ Clear",key="sb_clr",use_container_width=True): st.session_state.api_key=""; st.rerun()
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
        if st.button(_l,key=f"nav_{_l}",use_container_width=True): st.switch_page(_p)

if not st.session_state.get("user_id"):
    st.warning("Please complete onboarding on the Home page first."); st.stop()

uid=st.session_state.user_id
user=db.get_user(uid) or {}
gap=st.session_state.get("skill_gap") or {}
goal=db.get_active_goal(uid) or {}

page_header("Roadmap Generator","Your personalized step-by-step career plan","Roadmap Planner Agent")

col1,col2,col3=st.columns(3)
with col1: daily_hours=st.slider("Daily study hours",1,8,2)
with col2: career_target=st.text_input("Target Career",value=user.get("dream_career",""))
with col3: st.markdown(f"<br><p style='color:{TEXT_MUTED}'>Readiness: <strong>{(gap or {}).get('readiness_score',0)}%</strong></p>",unsafe_allow_html=True)

col1,col2=st.columns(2)
with col1:
    if st.button("🗺️ Generate Roadmap",use_container_width=True):
        if not career_target: st.error("Set target career first")
        else:
            with st.spinner("Planning your journey..."):
                try:
                    roadmap=RoadmapPlannerAgent().create_roadmap(career_target,gap,user,daily_hours,uid)
                    st.session_state["roadmap"]=roadmap
                    goal_id=st.session_state.get("active_goal_id") or goal.get("id",1)
                    db.save_roadmap(uid,goal_id,json.dumps(roadmap.get("plan_30_day",{})),json.dumps(roadmap.get("plan_90_day",{})),json.dumps(roadmap.get("plan_6_month",{})),json.dumps(roadmap.get("plan_1_year",{})),roadmap.get("key_milestones",[]))
                    st.success("✅ Done!"); st.rerun()
                except Exception as e: st.error(f"Error: {e}")
with col2:
    saved=db.get_latest_roadmap(uid)
    if saved:
        if st.button("📂 Load Saved",use_container_width=True):
            st.session_state["roadmap"]={"plan_30_day":json.loads(saved.get("plan_30_day","{}") or "{}"),"plan_90_day":json.loads(saved.get("plan_90_day","{}") or "{}"),"plan_6_month":json.loads(saved.get("plan_6_month","{}") or "{}"),"plan_1_year":json.loads(saved.get("plan_1_year","{}") or "{}"),"key_milestones":json.loads(saved.get("milestones","[]") or "[]")}
            st.rerun()

roadmap=st.session_state.get("roadmap")
if not roadmap: st.info("Click Generate to create your roadmap."); st.stop()
if "raw" in roadmap: st.markdown(roadmap["raw"]); st.stop()

st.markdown(f"## {roadmap.get('roadmap_title','Your Career Roadmap')}")

tabs=st.tabs(["🌱 30 Days","🔥 90 Days","🚀 6 Months","🏆 1 Year","📅 Weekly","🗓️ Milestones"])
plan_keys=["plan_30_day","plan_90_day","plan_6_month","plan_1_year"]
plan_colors=[(PRIMARY,"🌱"),(SECONDARY,"🔥"),(ACCENT,"🚀"),("#FFB84D","🏆")]

for tab,pk,(color,icon) in zip(tabs[:4],plan_keys,plan_colors):
    plan=roadmap.get(pk,{})
    with tab:
        if not plan: st.info("No data."); continue
        st.markdown(f"""<div style="background:linear-gradient(135deg,{color}20,{color}08);border:1px solid {color}40;border-radius:16px;padding:1.5rem;margin-bottom:1rem">
        <h3 style="margin:0;color:{color}">{icon} {plan.get('theme','')}</h3><p style="color:{TEXT_MUTED};margin:0.5rem 0 0">{plan.get('milestone','')}</p></div>""",unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            st.markdown("**🎯 Goals**")
            for g in plan.get("goals",[]): st.markdown(f"• {g}")
        with col2:
            for key in ["daily_tasks","projects_to_build","portfolio_items"]:
                items=plan.get(key,[])
                if items:
                    st.markdown(f"**{'⚡ Daily' if key=='daily_tasks' else '🔨 Projects' if key=='projects_to_build' else '📁 Portfolio'}**")
                    for item in items: st.markdown(f"• {item}")
            if plan.get("expected_outcome"): st.markdown(f"**🏆** {plan.get('expected_outcome','')}")

with tabs[4]:
    sched=roadmap.get("weekly_schedule",{})
    if sched:
        cols=st.columns(3)
        for i,(day,focus) in enumerate(sched.items()):
            with cols[i%3]:
                st.markdown(f"""<div style="background:{BG_CARD};border-radius:12px;padding:1rem;margin:0.3rem 0">
                <div style="font-weight:700">{day.title()}</div><div style="color:{TEXT_MUTED};font-size:0.9rem">{focus}</div></div>""",unsafe_allow_html=True)

with tabs[5]:
    milestones=roadmap.get("key_milestones",[])
    if isinstance(milestones,str):
        try: milestones=json.loads(milestones)
        except: milestones=[]
    if milestones: progress_timeline(milestones)
    else: st.info("No milestones found.")

st.download_button("📥 Download Roadmap",roadmap_to_markdown(roadmap,user.get("name","User"),career_target),file_name="roadmap.md",mime="text/markdown")
if st.button("▶️ Next: Learning Resources",use_container_width=True): st.switch_page("pages/05_Learning_Hub.py")
