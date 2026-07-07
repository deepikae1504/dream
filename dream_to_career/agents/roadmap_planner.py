"""
agents/roadmap_planner.py
Roadmap Planner Agent — creates 30-day / 90-day / 6-month / 1-year plans.
"""
import json
from agents.base_agent import BaseAgent
from config.prompts import ROADMAP_PLANNER_SYSTEM, ROADMAP_PROMPT


class RoadmapPlannerAgent(BaseAgent):
    name = "Roadmap Planner Agent"
    system_prompt = ROADMAP_PLANNER_SYSTEM

    def create_roadmap(
        self,
        dream_career: str,
        skill_gap: dict,
        user_profile: dict,
        daily_hours: int = 2,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns roadmap_title, total_duration_months,
        plan_30_day, plan_90_day, plan_6_month, plan_1_year,
        weekly_schedule, key_milestones.
        """
        top_gaps = skill_gap.get("skill_gaps", [])[:6]
        readiness = skill_gap.get("readiness_score", 0)

        prompt = ROADMAP_PROMPT.format(
            dream_career=dream_career,
            current_role=user_profile.get("current_role", "Fresher"),
            daily_hours=daily_hours,
            readiness_score=readiness,
            top_gaps=json.dumps(top_gaps),
        )
        return self._call_and_parse(prompt, user_id=user_id, action="create_roadmap")
