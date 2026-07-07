"""
config/settings.py
Runtime settings, Streamlit page config, and feature flags.
"""
import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent.parent
DB_PATH   = BASE_DIR / "dream_career.db"
LOGS_DIR  = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ── Gemini ─────────────────────────────────────────────────────────────────────
GEMINI_MODEL          = "gemini-2.0-flash-lite"
GEMINI_MAX_TOKENS     = 8192
GEMINI_TEMPERATURE    = 0.7
GEMINI_RETRY_COUNT    = 3
GEMINI_RETRY_DELAY_S  = 1.5   # seconds, doubles on each retry

# ── Streamlit page metadata ────────────────────────────────────────────────────
APP_TITLE       = "Dream-to-Career AI"
APP_ICON        = "🚀"
APP_LAYOUT      = "wide"
APP_MENU_ITEMS  = {
    "Get Help":     "https://github.com",
    "Report a bug": None,
    "About":        "# Dream-to-Career AI\nYour personal AI career coach.",
}

# ── Feature flags ──────────────────────────────────────────────────────────────
FEATURE_OBSERVABILITY   = True   # show agent trace expanders
FEATURE_EXPORT_PDF      = False  # PDF export (requires weasyprint)
FEATURE_FIREBASE        = False  # swap SQLite for Firebase

# ── Pagination / limits ────────────────────────────────────────────────────────
MAX_INTERVIEW_QUESTIONS = 10
MAX_PROGRESS_ROWS       = 200
MAX_AGENT_LOGS          = 500
MAX_WHATIF_HISTORY      = 20

# ── Session defaults ───────────────────────────────────────────────────────────
DEFAULT_DAILY_HOURS   = 2
DEFAULT_TIMELINE_MONTHS = 12

# ── Env key name ───────────────────────────────────────────────────────────────
GEMINI_KEY_ENV = "GEMINI_API_KEY"

def get_api_key(session_state=None) -> str:
    """
    Resolve Gemini API key from 3 sources (in priority order):
      1. Sidebar input stored in st.session_state  (runtime)
      2. .streamlit/secrets.toml                   (st.secrets)
      3. .env file / OS environment variable        (GEMINI_API_KEY)
    Returns empty string if not found anywhere.
    """
    # 1. Sidebar / session
    if session_state:
        key = session_state.get("api_key", "")
        if key:
            return key

    # 2. Streamlit secrets.toml
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    # 3. Environment variable (.env or system)
    return os.environ.get(GEMINI_KEY_ENV, "")
