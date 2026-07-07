"""
tools/career_tools.py
Domain tools used by agents: career lookups, skill scoring, goal tracking.
These are pure-Python functions — no LLM calls — so they're fast and deterministic.
"""
from __future__ import annotations
from config.constants import (
    SKILL_CATEGORIES, POPULAR_CAREERS, PROFICIENCY_LABELS,
    PLATFORM_ICONS, HEALTH_THRESHOLDS, HEALTH_LABELS,
)
from database import db


# ── Skill utilities ────────────────────────────────────────────────────────────

def get_all_skills_flat() -> list[str]:
    """Return every skill name from the taxonomy as a flat list."""
    return [s for skills in SKILL_CATEGORIES.values() for s in skills]


def get_skill_category(skill_name: str) -> str:
    """Return the category for a given skill, or 'Other'."""
    for category, skills in SKILL_CATEGORIES.items():
        if skill_name in skills:
            return category
    return "Other"


def proficiency_label(level: int) -> str:
    return PROFICIENCY_LABELS.get(level, "Unknown")


def score_skill_set(user_skills: list[dict], required_skills: list[dict]) -> float:
    """
    Simple coverage score: what fraction of required skills does the user have?
    Returns 0.0 – 100.0.
    """
    if not required_skills:
        return 0.0
    user_names = {
        s.get("skill_name", s.get("name", "")).lower() for s in user_skills
    }
    matched = sum(
        1 for rs in required_skills
        if (rs.get("skill", "") if isinstance(rs, dict) else rs).lower() in user_names
    )
    return round((matched / len(required_skills)) * 100, 1)


# ── Career lookup ──────────────────────────────────────────────────────────────

def search_popular_careers(query: str) -> list[str]:
    """Fuzzy-filter popular career presets by query string."""
    q = query.lower()
    return [c for c in POPULAR_CAREERS if q in c.lower()]


def get_platform_icon(platform: str) -> str:
    """Return the emoji icon for a learning platform."""
    for key, icon in PLATFORM_ICONS.items():
        if key in platform.lower():
            return icon
    return PLATFORM_ICONS["default"]


# ── Goal tracking ──────────────────────────────────────────────────────────────

def get_goal_progress_pct(user_id: int) -> float:
    """
    Rough progress percentage based on logged activity hours vs.
    an estimated target (assumes 2 hrs/day × 30 days as monthly target).
    """
    logs = db.get_progress(user_id, 30)
    total_hours = sum(float(l.get("hours_spent", 0)) for l in logs)
    target_hours = 60.0  # 2 hrs × 30 days
    return min(round((total_hours / target_hours) * 100, 1), 100.0)


def count_milestones(user_id: int) -> int:
    logs = db.get_progress(user_id)
    return sum(1 for l in logs if l.get("milestone_completed"))


def streak_days(user_id: int) -> int:
    """
    Count consecutive days (from today backwards) with ≥ 1 activity log.
    """
    from datetime import date, timedelta
    logs = db.get_progress(user_id, 60)
    active_dates = {l.get("date", "") for l in logs if l.get("hours_spent", 0) > 0}
    streak = 0
    day = date.today()
    while str(day) in active_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


# ── Health score helpers ───────────────────────────────────────────────────────

def get_health_grade(overall_score: float) -> tuple[str, str]:
    """Returns (letter_grade, color_hex) for a given overall score."""
    for level, threshold in [
        ("excellent", HEALTH_THRESHOLDS["excellent"]),
        ("good",      HEALTH_THRESHOLDS["good"]),
        ("average",   HEALTH_THRESHOLDS["average"]),
    ]:
        if overall_score >= threshold:
            return HEALTH_LABELS[level]
    return HEALTH_LABELS["poor"]


# ── Progress summary ───────────────────────────────────────────────────────────

def build_progress_summary(user_id: int) -> dict:
    """
    Quick summary dict consumed by the dashboard and accountability agent.
    """
    logs = db.get_progress(user_id, 30)
    health_rows = db.get_health_scores(user_id, 1)
    interviews  = db.get_interviews(user_id, 10)

    total_hours  = sum(float(l.get("hours_spent", 0)) for l in logs)
    milestones   = sum(1 for l in logs if l.get("milestone_completed"))
    active_days  = len({l.get("date", "") for l in logs if float(l.get("hours_spent", 0)) > 0})
    avg_int_score = (
        sum(i.get("overall_score", 0) for i in interviews) / len(interviews)
        if interviews else 0.0
    )

    latest_health = health_rows[0].get("overall_score", 0) if health_rows else 0
    grade, color  = get_health_grade(latest_health)

    return {
        "total_hours_30d":   round(total_hours, 1),
        "milestones_30d":    milestones,
        "active_days_30d":   active_days,
        "streak":            streak_days(user_id),
        "avg_interview":     round(avg_int_score, 1),
        "goal_progress_pct": get_goal_progress_pct(user_id),
        "health_score":      latest_health,
        "health_grade":      grade,
        "health_color":      color,
        "interviews_done":   len(interviews),
    }
