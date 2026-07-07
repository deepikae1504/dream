import streamlit as st
st.set_page_config(page_title="Learning Hub | Dream-to-Career AI", page_icon="📚", layout="wide")
import os
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, metric_card, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from agents.learning_coach import LearningCoachAgent
from config.constants import PLATFORM_ICONS, ACTIVITY_TYPES
from utils.validators import validate_progress_log

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
    _ch = st.selectbox("Model", _models, index=_models.index(_cur),
        label_visibility="collapsed", key="sb_model")
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
gap  = st.session_state.get("skill_gap") or {}

def get_icon(p):
    for k,v in PLATFORM_ICONS.items():
        if k in p.lower(): return v
    return "📌"

page_header("Learning Hub","Curated resources for your career path","Learning Coach Agent")

if st.button("🤖 Get AI-Curated Resources", use_container_width=True):
    if not gap:
        st.warning("Complete Skill Assessment first to get personalised resources.")
    else:
        with st.spinner("Finding the best resources for you..."):
            try:
                res = LearningCoachAgent().recommend_resources(gap, user.get("dream_career",""), uid)
                st.session_state["learning_resources"] = res
                flat = [{"skill":path.get("skill",""),"type":r.get("type","course"),
                    "title":r.get("title",""),"url":r.get("url",""),
                    "platform":r.get("platform",""),"free":r.get("free",True),
                    "priority":path.get("priority",1)}
                    for path in res.get("learning_path",[]) for r in path.get("resources",[])]
                db.save_resources(uid, flat)
                st.success("✅ Resources loaded!"); st.rerun()
            except Exception as e: st.error(f"Error: {e}")

resources = st.session_state.get("learning_resources")

if resources and "raw" not in resources:
    all_rs = [r for path in resources.get("learning_path",[]) for r in path.get("resources",[])]
    c1,c2,c3 = st.columns(3)
    with c1: metric_card("Learning Paths", str(len(resources.get("learning_path",[]))), icon="🗺️")
    with c2: metric_card("Total Resources", str(len(all_rs)), icon="📚")
    with c3: metric_card("Free", str(sum(1 for r in all_rs if r.get("free",True))), icon="🆓")

    daily = resources.get("daily_learning_plan",{})
    if daily:
        st.markdown("### ⏰ Daily Learning Routine")
        cc1,cc2,cc3 = st.columns(3)
        with cc1:
            st.markdown(f"""<div style="background:{BG_CARD};border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:1.5rem">🌅</div><div style="font-weight:600">Morning</div>
            <div style="color:{TEXT_MUTED};font-size:0.85rem">{daily.get('morning','')}</div></div>""",
            unsafe_allow_html=True)
        with cc2:
            st.markdown(f"""<div style="background:{BG_CARD};border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:1.5rem">💻</div><div style="font-weight:600">Main Session</div>
            <div style="color:{TEXT_MUTED};font-size:0.85rem">{daily.get('main_session','')}</div></div>""",
            unsafe_allow_html=True)
        with cc3:
            st.markdown(f"""<div style="background:{BG_CARD};border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:1.5rem">🌙</div><div style="font-weight:600">Evening</div>
            <div style="color:{TEXT_MUTED};font-size:0.85rem">{daily.get('evening','')}</div></div>""",
            unsafe_allow_html=True)

    st.markdown("### 📚 Your Learning Path")
    for path in resources.get("learning_path",[]):
        pri = path.get("priority",1)
        icon_p = "🔴" if pri==1 else ("🟡" if pri==2 else "🟢")
        with st.expander(f"{icon_p} Priority {pri}: {path.get('skill','')}", expanded=(pri==1)):
            for r in path.get("resources",[]):
                free_tag = "🆓 FREE" if r.get("free") else "💰 Paid"
                url = r.get("url","")
                link = f" — [Open ↗]({url})" if url.startswith("http") else ""
                st.markdown(f"**{get_icon(r.get('platform',''))} {r.get('title','')}** {free_tag}{link}")
                st.caption(f"{r.get('platform','')} · {r.get('duration','')} · {r.get('why_recommended','')}")
                st.markdown("---")
            for p in path.get("projects",[]):
                st.markdown(f"🔨 **{p.get('title','')}** — {p.get('description','')} `{p.get('difficulty','')}`")

    channels = resources.get("youtube_channels",[])
    if channels:
        st.markdown("### ▶️ YouTube Channels")
        cols = st.columns(3)
        for i,ch in enumerate(channels):
            with cols[i%3]:
                st.markdown(f"""<div style="background:{BG_CARD};border-radius:10px;padding:0.8rem;
                border:1px solid rgba(255,0,0,0.2)">▶️ {ch}</div>""", unsafe_allow_html=True)

    communities = resources.get("communities_to_join",[])
    if communities:
        st.markdown("### 🤝 Communities")
        for c in communities: st.markdown(f"• 🌐 {c}")
else:
    if not gap:
        st.info("👆 First complete **Skill Assessment**, then come back here for personalised resources.")
    else:
        st.info("Click **Get AI-Curated Resources** above to see your personalised learning plan.")

st.markdown("---")
st.markdown("### ✅ Log Today's Learning")
with st.form("log_form"):
    c1,c2 = st.columns(2)
    with c1:
        activity = st.selectbox("Activity", ACTIVITY_TYPES)
        hours = st.number_input("Hours spent", 0.0, 12.0, 1.0, 0.5)
    with c2:
        desc = st.text_area("What did you do?", height=80, placeholder="Describe what you studied...")
        milestone = st.checkbox("Completed a milestone 🏆")
    if st.form_submit_button("💾 Log Progress", use_container_width=True):
        ok,err = validate_progress_log(desc, hours)
        if not ok: st.error(err)
        else:
            db.log_progress(uid, activity, desc, hours, milestone)
            st.success("✅ Progress logged!"); st.balloons()
