"""
utils/session.py
Centralised Streamlit session-state manager.
Call `init_session()` at the top of every page to guarantee all keys exist.
"""
import streamlit as st
from database import db


# ── Default session schema ─────────────────────────────────────────────────────

_DEFAULTS: dict = {
    # Auth / profile
    "api_key":           "",
    "user_id":           None,
    "user_name":         "",
    "dream_career":      "",
    # Agent results (cached between reruns)
    "career_analysis":   None,
    "skill_gap":         None,
    "roadmap":           None,
    "learning_resources":None,
    "career_twin":       None,
    "recruiter_eval":    None,
    # Interview state machine
    "interview_active":       False,
    "interview_complete":     False,
    "interview_questions":    [],
    "interview_answers":      {},
    "interview_evaluations":  {},
    "interview_final_feedback": None,
    "interview_type":         "Technical",
    "current_q":              0,
    # What-If history
    "whatif_results":         [],
    "whatif_input":           "",
    # UI flags
    "show_past":              False,
    "show_observability":     False,
    "onboarding_complete":    False,
    # Goal
    "active_goal_id":         None,
    # Skill ratings (slider values keyed by skill name)
    "skill_ratings":          {},
}


def init_session() -> None:
    """Ensure every key in the schema exists in session_state."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def clear_interview_state() -> None:
    """Reset all interview-related keys so a fresh interview can start."""
    interview_keys = [
        "interview_active", "interview_complete", "interview_questions",
        "interview_answers", "interview_evaluations", "interview_final_feedback",
        "current_q",
    ]
    for k in interview_keys:
        st.session_state[k] = _DEFAULTS[k]


def clear_agent_cache() -> None:
    """Wipe all cached agent results (useful when switching career goals)."""
    agent_keys = [
        "career_analysis", "skill_gap", "roadmap",
        "learning_resources", "career_twin", "recruiter_eval",
    ]
    for k in agent_keys:
        st.session_state[k] = None


def get_user_profile() -> dict | None:
    """
    Fetch the full user profile from DB using the session user_id.
    Returns None if not logged in.
    """
    uid = st.session_state.get("user_id")
    if not uid:
        return None
    return db.get_user(uid)


def is_logged_in() -> bool:
    return bool(st.session_state.get("user_id"))


def login_gate(page_name: str = "this page") -> bool:
    """
    Show a warning and return False if the user is not logged in.
    Usage:
        if not login_gate("Career Analysis"):
            return
    """
    if not is_logged_in():
        st.warning(
            f"⚠️ You need to create your profile before accessing {page_name}. "
            f"Head over to the **Home** page to get started."
        )
        col1, _ = st.columns([1, 3])
        with col1:
            if st.button("🏠 Go to Home"):
                st.switch_page("pages/01_Home.py")
        return False
    return True


def set_user(user_id: int, name: str, dream_career: str) -> None:
    """Convenience setter after successful onboarding."""
    st.session_state.user_id     = user_id
    st.session_state.user_name   = name
    st.session_state.dream_career = dream_career
    st.session_state.onboarding_complete = True
