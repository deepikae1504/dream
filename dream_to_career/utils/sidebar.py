"""
utils/sidebar.py
Shared sidebar: API key input, profile snapshot, navigation.
"""
import os
import streamlit as st
from database import db
from utils.session import init_session, is_logged_in
from config.constants import COLORS
from config.settings import GEMINI_KEY_ENV

P  = COLORS["primary"]
S  = COLORS["secondary"]
A  = COLORS["accent"]
MT = COLORS["text_muted"]
BC = COLORS["bg_card"]

NAV_ITEMS = [
    ("pages/01_Home.py",                "🏠", "Home"),
    ("pages/02_Career_Analysis.py",     "🔭", "Career Analysis"),
    ("pages/03_Skill_Assessment.py",    "🧩", "Skill Assessment"),
    ("pages/04_Roadmap_Generator.py",   "🗺️", "Roadmap Generator"),
    ("pages/05_Learning_Hub.py",        "📚", "Learning Hub"),
    ("pages/06_AI_Career_Twin.py",      "🤖", "AI Career Twin"),
    ("pages/07_WhatIf_Simulator.py",    "⚡", "What-If Simulator"),
    ("pages/08_Mock_Interview.py",      "🎤", "Mock Interview"),
    ("pages/09_Progress_Dashboard.py",  "📈", "Progress Dashboard"),
    ("pages/10_Analytics.py",          "🔬", "Analytics & Admin"),
]


def _load_key_from_env():
    """Load API key from .env / os.environ into session_state on first run."""
    if st.session_state.get("api_key"):
        return  # already set

    # Try .streamlit/secrets.toml
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key and key != "AIzaSy_paste_your_key_here":
            st.session_state.api_key = key.strip()
            return
    except Exception:
        pass

    # Try environment variable / .env file
    key = os.environ.get(GEMINI_KEY_ENV, "")
    if key and key != "AIzaSy_paste_your_key_here":
        st.session_state.api_key = key.strip()


def render_sidebar():
    init_session()
    _load_key_from_env()   # pull from .env / secrets.toml on every render

    with st.sidebar:
        # ── Brand ────────────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:1rem 0 0.5rem">
            <div style="font-size:2rem">🚀</div>
            <div style="font-weight:700;font-size:1.1rem;
            background:linear-gradient(135deg,{P},{S});
            -webkit-background-clip:text;-webkit-text-fill-color:transparent">
                Dream-to-Career AI
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── API Key ───────────────────────────────────────────────────────────
        current_key = st.session_state.get("api_key", "")
        has_key     = bool(current_key)

        with st.expander(
            "🔑 API Key " + ("✅ Set" if has_key else "⚠️ Required"),
            expanded=not has_key,
        ):
            new_key = st.text_input(
                "Gemini API Key",
                value=current_key,
                type="password",
                placeholder="AIzaSy...",
                help="Get a free key at aistudio.google.com/app/apikey",
                label_visibility="collapsed",
                key="api_key_input",   # unique key — does NOT conflict with session key
            )

            if st.button("💾 Save Key", use_container_width=True, key="save_api_key"):
                cleaned = new_key.strip()
                if not cleaned:
                    st.error("Please paste your API key first.")
                elif len(cleaned) < 10:
                    st.error("Key seems too short. Please copy the full key.")
                else:
                    st.session_state.api_key = cleaned
                    st.success("✅ Key saved!")
                    st.rerun()

            if not has_key:
                st.caption("Get your free key → [aistudio.google.com](https://aistudio.google.com/app/apikey)")
            else:
                # Show masked key so user knows which key is active
                masked = current_key[:8] + "..." + current_key[-4:]
                st.caption(f"Active key: `{masked}`")
                if st.button("🗑️ Clear Key", use_container_width=True, key="clear_api_key"):
                    st.session_state.api_key = ""
                    st.rerun()

        # ── Model selector ────────────────────────────────────────────────────
        with st.expander("🤖 Gemini Model", expanded=False):
            model_options = [
                "gemini-1.5-flash",       # best free tier — recommended
                "gemini-1.5-flash-8b",    # fastest, most generous free tier
                "gemini-1.5-pro",         # smarter but lower free quota
                "gemini-2.0-flash",       # newest but strictest free quota
            ]
            current_model = st.session_state.get("gemini_model", "gemini-1.5-flash")
            if current_model not in model_options:
                current_model = "gemini-1.5-flash"

            selected = st.selectbox(
                "Model",
                model_options,
                index=model_options.index(current_model),
                label_visibility="collapsed",
                key="model_selector",
            )
            if selected != st.session_state.get("gemini_model"):
                st.session_state.gemini_model = selected
                st.rerun()

            st.caption(
                "💡 **gemini-1.5-flash** = best free tier\n\n"
                "**gemini-1.5-flash-8b** = highest free quota"
            )

        st.markdown("---")
        if is_logged_in():
            user = db.get_user(st.session_state.user_id) or {}
            st.markdown(f"""
            <div style="background:{BC};border:1px solid rgba(108,99,255,0.2);
            border-radius:12px;padding:1rem;margin-bottom:0.5rem">
                <div style="font-weight:700;font-size:0.95rem">👋 {user.get('name','')}</div>
                <div style="color:{MT};font-size:0.8rem;margin-top:0.3rem">
                    🎯 {user.get('dream_career','Not set')}
                </div>
                <div style="color:{MT};font-size:0.75rem;margin-top:0.2rem">
                    {user.get('current_role','')} · {user.get('experience_years',0)} yrs exp
                </div>
            </div>
            """, unsafe_allow_html=True)

            health_rows = db.get_health_scores(st.session_state.user_id, 1) or []
            if health_rows:
                score = health_rows[0].get("overall_score", 0)
                color = S if score >= 70 else (P if score >= 40 else A)
                st.markdown(f"""
                <div style="text-align:center;background:{color}15;
                border:1px solid {color}40;border-radius:10px;
                padding:0.5rem;margin-bottom:1rem">
                    <span style="color:{color};font-weight:700;font-size:1.1rem">{score:.0f}</span>
                    <span style="color:{MT};font-size:0.75rem"> / 100 Career Health</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Complete onboarding on the **Home** page first.")

        st.markdown("---")

        # ── Navigation ────────────────────────────────────────────────────────
        st.markdown(
            f"<div style='color:{MT};font-size:0.72rem;font-weight:600;"
            f"text-transform:uppercase;letter-spacing:0.06em;"
            f"margin-bottom:0.4rem'>Navigate</div>",
            unsafe_allow_html=True,
        )
        for path, icon, label in NAV_ITEMS:
            if st.button(f"{icon}  {label}", key=f"nav_{label}",
                         use_container_width=True):
                st.switch_page(path)

        st.markdown("---")
        st.markdown(
            f"<div style='text-align:center;color:{MT};font-size:0.68rem'>"
            f"Built with Gemini + Streamlit<br>v1.0 · Hackathon Edition</div>",
            unsafe_allow_html=True,
        )
