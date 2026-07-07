"""
pages/01_🏠_Home.py
Landing & onboarding page — the first thing every user sees.
Uses shared session/sidebar/validator modules instead of inline duplication.
"""
import streamlit as st
from database import db
from utils.session import init_session, set_user
from utils.sidebar import render_sidebar
from utils.ui_components import apply_styles, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from utils.validators import validate_name, validate_career, validate_email
from config.constants import EDUCATION_LEVELS, POPULAR_CAREERS

AGENT_SHOWCASE = [
    ("🔭", "Career Analyst",    "Deep market & career intelligence"),
    ("🧩", "Skill Gap Agent",   "Identify exactly what's missing"),
    ("🗺️", "Roadmap Planner",   "30-day to 1-year personalized plans"),
    ("📚", "Learning Coach",    "Curated free resources & projects"),
    ("🎤", "Interview Mentor",  "Mock interviews with AI feedback"),
    ("📊", "Accountability",    "Weekly health scores & motivation"),
    ("🤖", "AI Career Twin",    "Predict your future career outcomes"),
    ("⚡", "What-If Simulator", "Simulate different learning paths"),
]

HOW_IT_WORKS = [
    ("1", "Tell us your dream", "Enter your target career and current background"),
    ("2", "AI analyzes",        "9 specialized agents assess and plan your path"),
    ("3", "Get your roadmap",   "Day-by-day, month-by-month personalized plan"),
    ("4", "Track & improve",    "Weekly health scores, mock interviews, career twin"),
]


def _render_hero():
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem 2rem;">
        <div style="font-size:3.5rem;margin-bottom:0.5rem">🚀</div>
        <h1 style="font-size:3rem;margin:0;
            background:linear-gradient(135deg,{PRIMARY},{SECONDARY},{ACCENT});
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            font-weight:700;line-height:1.1">
            Dream-to-Career AI
        </h1>
        <p style="color:{TEXT_MUTED};font-size:1.1rem;margin:1rem auto;max-width:500px;">
            Your personal team of AI agents that turns your career dream into a
            step-by-step reality — tailored, trackable, and always on.
        </p>
    </div>
    """, unsafe_allow_html=True)


def _render_agent_showcase():
    cols = st.columns(4)
    for i, (icon, name, desc) in enumerate(AGENT_SHOWCASE):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="metric-card" style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
            border-radius:12px;padding:1rem;margin:0.3rem 0;text-align:center">
                <div style="font-size:1.8rem">{icon}</div>
                <div style="font-weight:600;font-size:0.85rem;margin:0.3rem 0">{name}</div>
                <div style="color:{TEXT_MUTED};font-size:0.75rem">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_welcome_back(user: dict):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(0,212,170,0.1),rgba(108,99,255,0.1));
    border:1px solid rgba(0,212,170,0.3);border-radius:16px;padding:1.5rem;text-align:center">
        <div style="font-size:1.5rem">👋</div>
        <h3 style="margin:0.3rem 0">Welcome back, {user['name']}!</h3>
        <p style="color:{TEXT_MUTED};margin:0">
            Dream Career: <strong style="color:{SECONDARY}">{user.get('dream_career','Not set yet')}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📈 View Dashboard", use_container_width=True):
            st.switch_page("pages/09_📈_Progress_Dashboard.py")
    with col2:
        if st.button("🗺️ My Roadmap", use_container_width=True):
            st.switch_page("pages/04_🗺️_Roadmap_Generator.py")
    with col3:
        if st.button("🤖 Career Twin", use_container_width=True):
            st.switch_page("pages/06_🤖_AI_Career_Twin.py")


def _render_onboarding_form():
    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.25);
    border-radius:20px;padding:2rem;margin-top:1rem">
        <h2 style="margin-top:0">✨ Start Your Journey</h2>
        <p style="color:{TEXT_MUTED}">Tell us about yourself and your dream career to get started.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("onboarding"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name *", placeholder="e.g. Arjun Sharma")
            current_role = st.text_input("Current Role", placeholder="e.g. Computer Science Student")
            experience = st.slider("Years of Experience", 0, 15, 0)
        with col2:
            dream = st.text_input(
                "Dream Career *", placeholder="e.g. AI/ML Engineer at Google",
                help=f"Popular picks: {', '.join(POPULAR_CAREERS[:4])}…",
            )
            education = st.selectbox("Education Level", EDUCATION_LEVELS)
            email = st.text_input("Email (optional)", placeholder="for saving progress")

        motivation = st.text_area(
            "Why this career? (optional)",
            placeholder="What excites you about this path...", height=80,
        )

        submitted = st.form_submit_button(
            "🚀 Launch My Career Journey", use_container_width=True
        )

        if submitted:
            name_ok, name_err = validate_name(name)
            career_ok, career_err = validate_career(dream)
            email_ok, email_err = validate_email(email)

            if not name_ok:
                st.error(name_err)
            elif not career_ok:
                st.error(career_err)
            elif not email_ok:
                st.error(email_err)
            else:
                with st.spinner("Setting up your AI career team..."):
                    uid = db.upsert_user(
                        name=name.strip(), email=email.strip(),
                        current_role=current_role.strip(),
                        experience_years=experience, education=education,
                        dream_career=dream.strip(),
                    )
                    set_user(uid, name.strip(), dream.strip())
                    if motivation:
                        db.save_career_goal(uid, dream.strip(), motivation=motivation.strip())
                st.success(f"🎉 Welcome, {name}! Your AI career team is ready.")
                st.balloons()
                st.rerun()


def _render_how_it_works():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### How it works")
    cols = st.columns(4)
    for i, (num, title, desc) in enumerate(HOW_IT_WORKS):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align:center;padding:1rem">
                <div style="background:linear-gradient(135deg,{PRIMARY},{SECONDARY});
                width:40px;height:40px;border-radius:50%;display:flex;align-items:center;
                justify-content:center;margin:0 auto 0.8rem;font-weight:700;color:white">
                    {num}
                </div>
                <div style="font-weight:600;margin-bottom:0.3rem">{title}</div>
                <div style="color:{TEXT_MUTED};font-size:0.8rem">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def render():
    init_session()
    apply_styles()

    _render_hero()
    _render_agent_showcase()
    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.get("user_id"):
        user = db.get_user(st.session_state.user_id)
        if user:
            _render_welcome_back(user)
            return

    _render_onboarding_form()
    _render_how_it_works()


# Allow this file to be run directly by Streamlit's multipage router
if __name__ == "__main__":
    render_sidebar()
    render()
