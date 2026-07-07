"""
agents/career_twin.py
AI Career Twin — predictive simulation of the learner's future career.
"""
from agents.base_agent import BaseAgent
from config.prompts import CAREER_TWIN_SYSTEM, CAREER_TWIN_PROMPT


class CareerTwinAgent(BaseAgent):
    name = "AI Career Twin"
    system_prompt = CAREER_TWIN_SYSTEM

    def predict_future(
        self,
        user_profile: dict,
        skills: list[dict],
        progress_logs: list[dict],
        health_score: dict | None,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns twin_name, current_trajectory, success_probability,
        predicted timelines, career_milestones_predicted,
        critical_risks, opportunities, missing_skills_for_success,
        competitive_advantage, twin_message.
        """
        skill_names = [s.get("skill_name", "") for s in skills]
        active_days = len(
            [p for p in progress_logs[-30:] if float(p.get("hours_spent", 0)) > 0]
        )
        h_score = health_score.get("overall_score", 0) if health_score else 0

        prompt = CAREER_TWIN_PROMPT.format(
            dream_career=user_profile.get("dream_career", "Not set"),
            current_role=user_profile.get("current_role", "Fresher"),
            skills=skill_names[:12],
            active_days=active_days,
            health_score=h_score,
        )
        return self._call_and_parse(
            prompt, user_id=user_id, action="predict_future"
        )
