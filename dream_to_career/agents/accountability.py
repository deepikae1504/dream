"""
agents/accountability.py
Accountability Agent — weekly career health scores and motivational planning.
"""
from agents.base_agent import BaseAgent
from config.prompts import (
    ACCOUNTABILITY_SYSTEM,
    HEALTH_SCORE_PROMPT,
    WEEKLY_PLAN_PROMPT,
)


class AccountabilityAgent(BaseAgent):
    name = "Accountability Agent"
    system_prompt = ACCOUNTABILITY_SYSTEM

    # ── Weekly health score ────────────────────────────────────────────────────

    def calculate_health_score(
        self,
        progress_logs: list[dict],
        interview_scores: list[float],
        user_profile: dict,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns learning_consistency, skill_development, project_building,
        interview_readiness, overall_score, grade, insights,
        this_week_focus, motivational_message, streak_days, areas_at_risk.
        """
        recent = progress_logs[-14:] if progress_logs else []

        total_hours   = sum(float(l.get("hours_spent", 0)) for l in recent)
        active_days   = len({l.get("date", "") for l in recent if l.get("hours_spent", 0) > 0})
        milestones    = sum(1 for l in recent if l.get("milestone_completed"))
        recent_types  = [l.get("activity_type", "") for l in recent[-5:]]

        prompt = HEALTH_SCORE_PROMPT.format(
            total_hours=total_hours,
            active_days=active_days,
            milestones=milestones,
            recent_activities=recent_types,
            interview_scores=interview_scores[-3:] if interview_scores else [],
            dream_career=user_profile.get("dream_career", "Not set"),
        )
        return self._call_and_parse(
            prompt, user_id=user_id, action="health_score"
        )

    # ── Weekly plan ────────────────────────────────────────────────────────────

    def generate_weekly_plan(
        self,
        health_score: dict,
        roadmap: dict,
        user_profile: dict,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns week_theme, daily_goals (7 days),
        weekly_challenge, accountability_check, reward.
        """
        roadmap_theme = (
            roadmap.get("plan_30_day", {}).get("theme", "Foundation Building")
            if roadmap else "Foundation Building"
        )
        prompt = WEEKLY_PLAN_PROMPT.format(
            health_scores=health_score,
            roadmap_theme=roadmap_theme,
            dream_career=user_profile.get("dream_career", "Not set"),
        )
        return self._call_and_parse(
            prompt, user_id=user_id, action="weekly_plan"
        )

    # ── Motivational nudge ────────────────────────────────────────────────────

    def generate_nudge(
        self,
        days_inactive: int,
        dream_career: str,
        user_id: int | None = None,
    ) -> str:
        """Short motivational message after N days of inactivity."""
        prompt = (
            f"Write a short, personal, non-clichéd motivational message (2-3 sentences) "
            f"for someone who wants to become a {dream_career} but hasn't studied for "
            f"{days_inactive} days. Do NOT use generic phrases like 'you've got this'."
        )
        return self._call(prompt, user_id=user_id, action="nudge")
