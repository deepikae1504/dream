"""
pages/01_Home.py  —  redirects to app.py / acts as Streamlit multipage stub
"""
import streamlit as st
st.set_page_config(page_title="Home | Dream-to-Career AI", page_icon="🚀", layout="wide")
from database.db import init_db
from utils.session import init_session, set_user
from utils.sidebar import render_sidebar
from utils.ui_components import apply_styles, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from utils.validators import validate_name, validate_career, validate_email
from config.constants import EDUCATION_LEVELS, POPULAR_CAREERS
from database import db

init_db(); init_session(); apply_styles(); render_sidebar()

AGENT_SHOWCASE = [
    ("🔭","Career Analyst","Deep market & career intelligence"),
    ("🧩","Skill Gap Agent","Identify exactly what's missing"),
    ("🗺️","Roadmap Planner","30-day to 1-year personalized plans"),
    ("📚","Learning Coach","Curated free resources & projects"),
    ("🎤","Interview Mentor","Mock interviews with AI feedback"),
    ("📊","Accountability","Weekly health scores & motivation"),
    ("🤖","AI Career Twin","Predict your future career outcomes"),
    ("⚡","What-If Simulator","Simulate different learning paths"),
]

st.markdown(f"""
<div style="text-align:center;padding:2.5rem 1rem 1.5rem">
  <div style="font-size:3rem">🚀</div>
  <h1 style="font-size:2.8rem;margin:0;background:linear-gradient(135deg,{PRIMARY},{SECONDARY},{ACCENT});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700">
    Dream-to-Career AI
  </h1>
  <p style="color:{TEXT_MUTED};font-size:1.05rem;margin:0.8rem auto;max-width:480px">
    Your personal team of AI agents that turns your career dream into a step-by-step reality.
  </p>
</div>""", unsafe_allow_html=True)

cols = st.columns(4)
for i,(icon,name,desc) in enumerate(AGENT_SHOWCASE):
    with cols[i%4]:
        st.markdown(f"""<div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
        border-radius:12px;padding:1rem;margin:0.3rem 0;text-align:center">
        <div style="font-size:1.6rem">{icon}</div>
        <div style="font-weight:600;font-size:0.82rem;margin:0.25rem 0">{name}</div>
        <div style="color:{TEXT_MUTED};font-size:0.73rem">{desc}</div></div>""",
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.get("user_id"):
    user = db.get_user(st.session_state.user_id)
    if user:
        st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(0,212,170,0.1),rgba(108,99,255,0.1));
        border:1px solid rgba(0,212,170,0.3);border-radius:16px;padding:1.5rem;text-align:center">
        <h3 style="margin:0.3rem 0">👋 Welcome back, {user['name']}!</h3>
        <p style="color:{TEXT_MUTED};margin:0">Dream Career: <strong style="color:{SECONDARY}">
        {user.get('dream_career','Not set yet')}</strong></p></div>""", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("📈 Dashboard", use_container_width=True):
                st.switch_page("pages/09_Progress_Dashboard.py")
        with c2:
            if st.button("🗺️ Roadmap", use_container_width=True):
                st.switch_page("pages/04_Roadmap_Generator.py")
        with c3:
            if st.button("🤖 Career Twin", use_container_width=True):
                st.switch_page("pages/06_AI_Career_Twin.py")
        st.stop()

st.markdown(f"""<div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.25);
border-radius:20px;padding:2rem;margin-top:1rem">
<h2 style="margin-top:0">✨ Start Your Journey</h2>
<p style="color:{TEXT_MUTED}">Tell us about yourself and your dream career.</p></div>""",
unsafe_allow_html=True)

with st.form("onboarding"):
    c1,c2 = st.columns(2)
    with c1:
        name         = st.text_input("Your Name *", placeholder="e.g. Arjun Sharma")
        current_role = st.text_input("Current Role", placeholder="e.g. CS Student")
        experience   = st.slider("Years of Experience", 0, 15, 0)
    with c2:
        dream     = st.text_input("Dream Career *", placeholder="e.g. AI/ML Engineer",
                                  help=f"Popular: {', '.join(POPULAR_CAREERS[:4])}…")
        education = st.selectbox("Education Level", EDUCATION_LEVELS)
        email     = st.text_input("Email (optional)")
    motivation = st.text_area("Why this career? (optional)", height=70)
    submitted  = st.form_submit_button("🚀 Launch My Career Journey", use_container_width=True)

if submitted:
    ok_n,err_n = validate_name(name)
    ok_c,err_c = validate_career(dream)
    ok_e,err_e = validate_email(email)
    if not ok_n: st.error(err_n)
    elif not ok_c: st.error(err_c)
    elif not ok_e: st.error(err_e)
    else:
        with st.spinner("Setting up your AI career team..."):
            uid = db.upsert_user(name.strip(), email.strip(), current_role.strip(),
                                 experience, education, dream.strip())
            set_user(uid, name.strip(), dream.strip())
            if motivation.strip():
                db.save_career_goal(uid, dream.strip(), motivation=motivation.strip())
        st.success(f"🎉 Welcome, {name}! Your AI career team is ready.")
        st.balloons()
        st.rerun()
