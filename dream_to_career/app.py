"""
app.py  —  Dream-to-Career AI  |  streamlit run app.py
"""
import os

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st

st.set_page_config(
    page_title="Dream-to-Career AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.db import init_db
from utils.session import init_session, set_user
from utils.ui_components import apply_styles, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from utils.validators import validate_name, validate_career, validate_email
from config.constants import EDUCATION_LEVELS, POPULAR_CAREERS
from database import db

init_db()
init_session()
apply_styles()

# ── SIDEBAR — built directly here, no import needed ───────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:0.5rem 0'>
        <div style='font-size:2rem'>🚀</div>
        <div style='font-weight:700;font-size:1.1rem;color:{PRIMARY}'>
            Dream-to-Career AI
        </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    # ── API KEY INPUT ─────────────────────────────────────────────────────────
    st.markdown("### 🔑 Gemini API Key")

    # Auto-load from environment
    if not st.session_state.get("api_key"):
        env_key = os.environ.get("GEMINI_API_KEY", "")
        if env_key:
            st.session_state.api_key = env_key
        try:
            secret_key = st.secrets.get("GEMINI_API_KEY", "")
            if secret_key:
                st.session_state.api_key = secret_key
        except Exception:
            pass

    typed_key = st.text_input(
        "Paste your key here",
        value=st.session_state.get("api_key", ""),
        type="password",
        placeholder="Paste your Gemini API key...",
        key="api_key_box",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Save", use_container_width=True, key="btn_save_key"):
            if typed_key and len(typed_key.strip()) > 5:
                st.session_state.api_key = typed_key.strip()
                st.success("Saved!")
                st.rerun()
            else:
                st.error("Please paste your key first")
    with col2:
        if st.button("🗑️ Clear", use_container_width=True, key="btn_clear_key"):
            st.session_state.api_key = ""
            st.rerun()

    if st.session_state.get("api_key"):
        k = st.session_state.api_key
        st.success(f"✅ Key active: {k[:6]}...{k[-4:]}")
    else:
        st.warning("⚠️ No key set — agents won't work")
        st.caption("Get free key → aistudio.google.com")

    st.markdown("---")

    # ── MODEL SELECTOR ────────────────────────────────────────────────────────
    st.markdown("### 🤖 Gemini Model")
    models = [
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash-8b-latest",
        "gemini-2.0-flash",
        "gemini-1.5-pro-latest",
    ]
    current_model = st.session_state.get("gemini_model", "gemini-2.0-flash-lite")
    if current_model not in models:
        current_model = "gemini-2.0-flash-lite"

    chosen = st.selectbox(
        "Select model",
        models,
        index=models.index(current_model),
        key="model_box",
        label_visibility="collapsed",
    )
    if chosen != st.session_state.get("gemini_model"):
        st.session_state.gemini_model = chosen
        st.rerun()
    st.caption("💡 gemini-2.0-flash-lite = most free quota")

    st.markdown("---")

    # ── NAVIGATION ────────────────────────────────────────────────────────────
    st.markdown("### 📍 Pages")
    pages = [
        ("pages/01_Home.py",               "🏠 Home"),
        ("pages/02_Career_Analysis.py",    "🔭 Career Analysis"),
        ("pages/03_Skill_Assessment.py",   "🧩 Skill Assessment"),
        ("pages/04_Roadmap_Generator.py",  "🗺️ Roadmap Generator"),
        ("pages/05_Learning_Hub.py",       "📚 Learning Hub"),
        ("pages/06_AI_Career_Twin.py",     "🤖 AI Career Twin"),
        ("pages/07_WhatIf_Simulator.py",   "⚡ What-If Simulator"),
        ("pages/08_Mock_Interview.py",     "🎤 Mock Interview"),
        ("pages/09_Progress_Dashboard.py", "📈 Progress Dashboard"),
        ("pages/10_Analytics.py",          "🔬 Analytics"),
    ]
    for path, label in pages:
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.switch_page(path)

# ── MAIN PAGE CONTENT ─────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:2rem 1rem 1rem'>
    <div style='font-size:3rem'>🚀</div>
    <h1 style='font-size:2.5rem;margin:0;
        background:linear-gradient(135deg,{PRIMARY},{SECONDARY},{ACCENT});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700'>
        Dream-to-Career AI
    </h1>
    <p style='color:{TEXT_MUTED};font-size:1rem;margin:0.8rem auto;max-width:480px'>
        Your personal team of AI agents that turns your career dream into a step-by-step reality.
    </p>
</div>
""", unsafe_allow_html=True)

AGENTS = [
    ("🔭","Career Analyst","Market intelligence"),
    ("🧩","Skill Gap Agent","Find what's missing"),
    ("🗺️","Roadmap Planner","30-day to 1-year plan"),
    ("📚","Learning Coach","Free resources & projects"),
    ("🎤","Interview Mentor","Mock interview feedback"),
    ("📊","Accountability","Weekly health scores"),
    ("🤖","AI Career Twin","Predict your future"),
    ("⚡","What-If Simulator","Simulate choices"),
]
cols = st.columns(4)
for i, (icon, name, desc) in enumerate(AGENTS):
    with cols[i % 4]:
        st.markdown(f"""
        <div style='background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
        border-radius:12px;padding:1rem;margin:0.3rem 0;text-align:center'>
            <div style='font-size:1.6rem'>{icon}</div>
            <div style='font-weight:600;font-size:0.82rem;margin:0.2rem 0'>{name}</div>
            <div style='color:{TEXT_MUTED};font-size:0.72rem'>{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Returning user
if st.session_state.get("user_id"):
    user = db.get_user(st.session_state.user_id) or {}
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(0,212,170,0.1),rgba(108,99,255,0.1));
    border:1px solid rgba(0,212,170,0.3);border-radius:16px;padding:1.5rem;text-align:center'>
        <h3 style='margin:0.3rem 0'>👋 Welcome back, {user.get('name','')}!</h3>
        <p style='color:{TEXT_MUTED};margin:0'>
            Dream Career: <strong style='color:{SECONDARY}'>{user.get('dream_career','Not set')}</strong>
        </p>
    </div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
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

# New user onboarding
st.markdown("## ✨ Start Your Journey")
with st.form("onboarding"):
    c1, c2 = st.columns(2)
    with c1:
        name         = st.text_input("Your Name *", placeholder="e.g. Arjun Sharma")
        current_role = st.text_input("Current Role", placeholder="e.g. CS Student")
        experience   = st.slider("Years of Experience", 0, 15, 0)
    with c2:
        dream     = st.text_input("Dream Career *", placeholder="e.g. AI Engineer")
        education = st.selectbox("Education Level", EDUCATION_LEVELS)
        email     = st.text_input("Email (optional)")
    motivation = st.text_area("Why this career? (optional)", height=70)
    submitted  = st.form_submit_button("🚀 Launch My Career Journey", use_container_width=True)

if submitted:
    ok_n, err_n = validate_name(name)
    ok_c, err_c = validate_career(dream)
    ok_e, err_e = validate_email(email)
    if   not ok_n: st.error(err_n)
    elif not ok_c: st.error(err_c)
    elif not ok_e: st.error(err_e)
    else:
        with st.spinner("Setting up your AI career team..."):
            uid = db.upsert_user(name.strip(), email.strip(),
                                 current_role.strip(), experience,
                                 education, dream.strip())
            set_user(uid, name.strip(), dream.strip())
            if motivation.strip():
                db.save_career_goal(uid, dream.strip(), motivation=motivation.strip())
        st.success(f"🎉 Welcome, {name}!")
        st.balloons()
        st.rerun()
