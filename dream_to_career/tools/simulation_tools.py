"""
tools/simulation_tools.py
Deterministic helpers for the What-If Simulator and Career Twin.
No LLM — fast, predictable, testable.
"""
from __future__ import annotations
import math


# ── Study-hours impact model ───────────────────────────────────────────────────

def estimated_months_to_ready(
    readiness_score: float,
    daily_hours: float,
    skill_gap_count: int,
) -> float:
    """
    Estimate months to career-readiness given current score and study pace.

    Model:
      - Each 1 point of readiness needs ~0.5 hours of focused study.
      - (100 - readiness_score) * 0.5 / (daily_hours * 30)
      - Capped at 24 months minimum 1 month.
    """
    deficit_hours = (100 - readiness_score) * 0.5
    if daily_hours <= 0:
        return 24.0
    months = deficit_hours / (daily_hours * 30)
    return round(min(max(months, 1.0), 24.0), 1)


def hours_impact(
    current_hours: float,
    new_hours: float,
    current_timeline_months: float,
) -> dict:
    """
    Calculate the timeline change when daily study hours change.
    """
    if current_hours <= 0 or new_hours <= 0:
        return {"delta_months": 0, "new_timeline": current_timeline_months}
    ratio = current_hours / new_hours
    new_timeline = round(current_timeline_months * ratio, 1)
    delta = round(new_timeline - current_timeline_months, 1)
    return {
        "delta_months": delta,
        "new_timeline": new_timeline,
        "direction": "faster" if delta < 0 else "slower",
    }


# ── Probability model ──────────────────────────────────────────────────────────

def success_probability(
    readiness_score: float,
    health_score: float,
    streak: int,
    interview_avg: float,
) -> float:
    """
    Weighted probability estimate (0-100).
      readiness     : 40 %
      health_score  : 30 %
      streak/30     : 10 %   (normalised to 0-100)
      interview_avg : 20 %
    """
    streak_norm = min(streak / 30 * 100, 100)
    interview_norm = interview_avg * 10  # 0-10 → 0-100
    prob = (
        0.40 * readiness_score
        + 0.30 * health_score
        + 0.10 * streak_norm
        + 0.20 * interview_norm
    )
    return round(min(max(prob, 0), 100), 1)


# ── What-if scenario helpers ───────────────────────────────────────────────────

def scenario_probability_delta(
    scenario_keyword: str,
    current_prob: float,
) -> float:
    """
    Rule-based probability delta for well-known scenario keywords.
    The LLM will override this with nuanced analysis, but this gives an
    instant preview before the API call.
    """
    deltas = {
        "4 hours": +12,
        "skip dsa": -18,
        "skip data structures": -18,
        "only ai": -8,
        "apply now": -5,
        "build projects": +10,
        "certification": +5,
        "bootcamp": +7,
        "break": -15,
        "open source": +8,
        "networking": +6,
        "freelance": +3,
    }
    low = scenario_keyword.lower()
    total_delta = sum(v for k, v in deltas.items() if k in low)
    new_prob = round(min(max(current_prob + total_delta, 5), 98), 1)
    return new_prob - current_prob


# ── Career Twin projections ────────────────────────────────────────────────────

def project_salary(
    current_readiness: float,
    target_career: str,
    months_ahead: int = 12,
) -> dict:
    """
    Very rough salary projection band for Indian tech market.
    """
    base_ranges = {
        "ai":        (8,  18),
        "ml":        (8,  18),
        "data scien": (7, 16),
        "full stack": (5, 14),
        "backend":   (5,  13),
        "frontend":  (4,  12),
        "cloud":     (7,  18),
        "devops":    (6,  16),
        "cyber":     (6,  15),
        "product":   (8,  20),
        "default":   (4,  12),
    }
    tc = target_career.lower()
    low, high = next(
        (v for k, v in base_ranges.items() if k in tc),
        base_ranges["default"],
    )
    # Scale by readiness
    scale = readiness_scale = min(readiness_current := (current_readiness / 100), 1.0)
    entry_low  = round(low  * max(scale, 0.5), 1)
    entry_high = round(high * max(scale, 0.7), 1)
    growth_3yr = round(entry_high * 1.6, 1)
    return {
        "entry_low_lpa":  entry_low,
        "entry_high_lpa": entry_high,
        "3yr_high_lpa":   growth_3yr,
        "formatted_entry": f"₹{entry_low}–{entry_high} LPA",
        "formatted_3yr":   f"₹{entry_high}–{growth_3yr} LPA",
    }


def risk_level(days_inactive: int, health_score: float) -> str:
    """
    Classify career-risk level based on inactivity and health score.
    """
    if days_inactive > 14 or health_score < 30:
        return "High"
    if days_inactive > 7 or health_score < 50:
        return "Medium"
    return "Low"
