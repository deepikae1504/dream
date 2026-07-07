"""
utils/exporters.py
Generate downloadable text/CSV content for roadmaps, reports, progress logs.
All functions return a str ready for st.download_button().
"""
from __future__ import annotations
import json
import csv
import io
from datetime import datetime


# ── Roadmap Markdown ───────────────────────────────────────────────────────────

def roadmap_to_markdown(roadmap: dict, user_name: str, career: str) -> str:
    lines = [
        f"# Career Roadmap: {roadmap.get('roadmap_title', career)}",
        f"**Generated for:** {user_name}",
        f"**Date:** {datetime.today().strftime('%B %d, %Y')}",
        f"**Total Duration:** {roadmap.get('total_duration_months', 12)} months",
        "",
    ]

    phase_map = [
        ("plan_30_day",  "30-Day Plan — Foundation"),
        ("plan_90_day",  "90-Day Plan — Core Skills"),
        ("plan_6_month", "6-Month Plan — Portfolio"),
        ("plan_1_year",  "1-Year Plan — Job Ready"),
    ]

    for key, heading in phase_map:
        plan = roadmap.get(key, {})
        if not plan:
            continue
        lines += [
            f"## {heading}",
            f"**Theme:** {plan.get('theme', '')}",
            f"**Milestone:** {plan.get('milestone', '')}",
            "",
            "### Goals",
        ]
        for g in plan.get("goals", []):
            lines.append(f"- {g}")

        if "daily_tasks" in plan:
            lines += ["", "### Daily Tasks"]
            for t in plan.get("daily_tasks", []):
                lines.append(f"- {t}")

        if "projects_to_build" in plan:
            lines += ["", "### Projects to Build"]
            for p in plan.get("projects_to_build", []):
                lines.append(f"- {p}")

        lines.append("")

    # Key milestones
    milestones = roadmap.get("key_milestones", [])
    if milestones:
        lines += ["## Key Milestones", ""]
        for m in milestones:
            lines.append(
                f"- **Month {m.get('month', '?')}:** "
                f"{m.get('milestone', '')} — {m.get('metric', '')}"
            )

    # Weekly schedule
    sched = roadmap.get("weekly_schedule", {})
    if sched:
        lines += ["", "## Weekly Schedule", ""]
        for day, focus in sched.items():
            lines.append(f"- **{day.title()}:** {focus}")

    return "\n".join(lines)


# ── Career analysis Markdown ───────────────────────────────────────────────────

def career_analysis_to_markdown(analysis: dict, career: str) -> str:
    lines = [
        f"# Career Analysis: {analysis.get('career_title', career)}",
        f"**Date:** {datetime.today().strftime('%B %d, %Y')}",
        "",
        f"## Overview",
        analysis.get("overview", ""),
        "",
        f"**Market Demand:** {analysis.get('market_demand', '')}",
        f"**Salary Range:** {analysis.get('avg_salary_range', '')}",
        "",
        "## Required Skills",
    ]
    for s in analysis.get("required_skills", []):
        if isinstance(s, dict):
            lines.append(f"- **{s.get('skill','')}** ({s.get('category','')}) — {s.get('priority','')}")
        else:
            lines.append(f"- {s}")

    lines += ["", "## Career Stages"]
    for stage in analysis.get("career_stages", []):
        if isinstance(stage, dict):
            lines.append(
                f"- **{stage.get('stage','')}** ({stage.get('timeline','')}) — {stage.get('salary','')}"
            )

    lines += [
        "", "## Top Companies",
        ", ".join(analysis.get("top_companies", [])),
        "", "## Growth Outlook",
        analysis.get("growth_outlook", ""),
        "", "## Success Factors",
    ]
    for f in analysis.get("success_factors", []):
        lines.append(f"- {f}")
    lines += ["", "## Challenges"]
    for c in analysis.get("challenges", []):
        lines.append(f"- {c}")

    return "\n".join(lines)


# ── Progress CSV ───────────────────────────────────────────────────────────────

def progress_to_csv(progress_logs: list[dict]) -> str:
    if not progress_logs:
        return "No progress logs found."

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["date", "activity_type", "description", "hours_spent",
                    "milestone_completed", "notes"],
        extrasaction="ignore",
    )
    writer.writeheader()
    for row in progress_logs:
        writer.writerow(row)

    return output.getvalue()


# ── Interview report Markdown ──────────────────────────────────────────────────

def interview_to_markdown(
    interview: dict,
    questions: list[dict],
    evaluations: dict[int, dict],
    overall_feedback: dict,
) -> str:
    lines = [
        "# Mock Interview Report",
        f"**Type:** {interview.get('interview_type', '')}",
        f"**Date:** {interview.get('created_at', datetime.today().strftime('%Y-%m-%d'))[:10]}",
        f"**Overall Score:** {interview.get('overall_score', 0):.1f}/10",
        f"**Performance:** {overall_feedback.get('performance_level', '')}",
        "",
        "## Overall Feedback",
        overall_feedback.get("overall_feedback", ""),
        "",
        "### Strengths",
    ]
    for s in overall_feedback.get("top_strengths", []):
        lines.append(f"- {s}")
    lines += ["", "### Areas to Improve"]
    for i in overall_feedback.get("critical_improvements", []):
        lines.append(f"- {i}")
    lines += ["", "### Next Steps"]
    for step in overall_feedback.get("next_steps", []):
        lines.append(f"1. {step}")

    lines += ["", "---", "## Question-by-Question Breakdown", ""]
    for idx, q in enumerate(questions):
        ev = evaluations.get(idx, {})
        lines += [
            f"### Q{idx + 1}: {q.get('question', '')}",
            f"**Score:** {ev.get('score', 0)}/10 — {ev.get('verdict', '')}",
            f"**Feedback:** {ev.get('feedback', '')}",
            "",
        ]

    return "\n".join(lines)


# ── Full profile JSON snapshot ─────────────────────────────────────────────────

def profile_snapshot(
    user: dict,
    skills: list[dict],
    goal: dict | None,
    health: dict | None,
) -> str:
    snapshot = {
        "exported_at": datetime.now().isoformat(),
        "user":        user,
        "skills":      skills,
        "active_goal": goal,
        "latest_health_score": health,
    }
    return json.dumps(snapshot, indent=2, default=str)
