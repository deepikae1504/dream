"""
agents/career_analyst.py
Career Analyst Agent — analyses a target career, market demand, required skills.
"""
from agents.base_agent import BaseAgent
from config.prompts import CAREER_ANALYST_SYSTEM, CAREER_ANALYSIS_PROMPT


class CareerAnalystAgent(BaseAgent):
    name = "Career Analyst Agent"
    system_prompt = CAREER_ANALYST_SYSTEM

    def analyze(
        self,
        dream_career: str,
        user_profile: dict,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns a structured career analysis dict with keys:
        career_title, overview, market_demand, avg_salary_range,
        required_skills, career_stages, top_companies, growth_outlook,
        key_certifications, daily_work, success_factors, challenges.
        """
        prompt = CAREER_ANALYSIS_PROMPT.format(
            dream_career=dream_career,
            current_role=user_profile.get("current_role", "Fresher / Student"),
            experience_years=user_profile.get("experience_years", 0),
            education=user_profile.get("education", "Not specified"),
        )
        return self._call_and_parse(prompt, user_id=user_id, action="analyze_career")
