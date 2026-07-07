"""
tools/assessment_tools.py
Pure-Python assessment helpers: scoring, skill-level mapping,
readiness matrix builder — no LLM calls.
"""
from __future__ import annotations
from config.constants import PROFICIENCY_LABELS, PRIORITY_COLORS


# ── Skill level mapping ────────────────────────────────────────────────────────

def slider_to_proficiency(value: int) -> str:
    """Convert a 0-5 slider value to a proficiency label."""
    return PROFICIENCY_LABELS.get(value, "Unknown")


def proficiency_to_score(level: int) -> float:
    """Map 0-5 proficiency to a 0-100 score for radar charts."""
    return level * 20.0


# ── Gap matrix ─────────────────────────────────────────────────────────────────

def build_gap_matrix(
    user_skill_ratings: dict[str, int],
    required_skills: list[dict],
) -> list[dict]:
    """
    Build a skill-gap matrix row for every required skill.

    Parameters
    ----------
    user_skill_ratings  : {skill_name: 0-5 level}
    required_skills     : [{skill, category, priority, level}]

    Returns
    -------
    List of rows:
      skill, category, required_level_label, user_level,
      gap_size (0-5), priority, status (OK|Gap|Missing)
    """
    level_map = {"Beginner": 1, "Intermediate": 3, "Advanced": 5}
    matrix = []

    for rs in required_skills:
        if not isinstance(rs, dict):
            continue
        name       = rs.get("skill", "")
        category   = rs.get("category", "Technical")
        priority   = rs.get("priority", "Medium")
        req_label  = rs.get("level", "Intermediate")
        req_level  = level_map.get(req_label, 3)
        user_level = user_skill_ratings.get(name, 0)
        gap        = max(0, req_level - user_level)

        if user_level == 0:
            status = "Missing"
        elif gap == 0:
            status = "OK"
        else:
            status = "Gap"

        matrix.append({
            "skill":             name,
            "category":          category,
            "required_level":    req_label,
            "user_level":        user_level,
            "user_level_label":  PROFICIENCY_LABELS.get(user_level, "Not known"),
            "gap_size":          gap,
            "priority":          priority,
            "priority_color":    PRIORITY_COLORS.get(priority, "#8890B5"),
            "status":            status,
        })

    # Sort: Missing first, then by gap size descending
    matrix.sort(key=lambda r: (r["status"] != "Missing", -r["gap_size"]))
    return matrix


# ── Readiness score ────────────────────────────────────────────────────────────

def calculate_local_readiness(
    user_skill_ratings: dict[str, int],
    required_skills: list[dict],
) -> float:
    """
    Compute a 0–100 readiness score purely from local data
    (no LLM required).  Used as a quick preview before the AI assessment.
    """
    if not required_skills:
        return 0.0
    level_map = {"Beginner": 1, "Intermediate": 3, "Advanced": 5}
    total_gap = 0
    total_possible = 0

    for rs in required_skills:
        if not isinstance(rs, dict):
            continue
        req_level  = level_map.get(rs.get("level", "Intermediate"), 3)
        user_level = user_skill_ratings.get(rs.get("skill", ""), 0)
        total_gap      += max(0, req_level - user_level)
        total_possible += req_level

    if total_possible == 0:
        return 0.0
    return round(max(0.0, (1 - total_gap / total_possible) * 100), 1)


# ── Interview scoring ──────────────────────────────────────────────────────────

def aggregate_interview_scores(evaluations: dict[int, dict]) -> dict:
    """
    Aggregate per-question evaluations into a summary.

    Parameters
    ----------
    evaluations : {question_index: {score, verdict, ...}}

    Returns
    -------
    {avg_score, min_score, max_score, total_questions, answered}
    """
    scores = [ev.get("score", 0) for ev in evaluations.values()]
    if not scores:
        return {"avg_score": 0, "min_score": 0, "max_score": 0,
                "total_questions": 0, "answered": 0}
    return {
        "avg_score":       round(sum(scores) / len(scores), 2),
        "min_score":       min(scores),
        "max_score":       max(scores),
        "total_questions": len(evaluations),
        "answered":        len([s for s in scores if s > 0]),
    }


# ── Skill chart data ───────────────────────────────────────────────────────────

def radar_data_from_ratings(
    ratings: dict[str, int],
    max_skills: int = 8,
) -> tuple[list[str], list[float]]:
    """
    Pick the top-N rated skills and return (labels, values) for a radar chart.
    Values are scaled to 0-100.
    """
    sorted_skills = sorted(
        [(k, v) for k, v in ratings.items() if v > 0],
        key=lambda x: -x[1],
    )[:max_skills]
    labels = [s[0] for s in sorted_skills]
    values = [s[1] * 20.0 for s in sorted_skills]
    return labels, values
