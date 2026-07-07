"""
agents/skill_gap.py
Skill Gap Agent — compares user skills vs. career requirements.
"""
import json
from agents.base_agent import BaseAgent
from config.prompts import SKILL_GAP_SYSTEM, SKILL_GAP_PROMPT


class SkillGapAgent(BaseAgent):
    name = "Skill Gap Agent"
    system_prompt = SKILL_GAP_SYSTEM

    # ── Main gap analysis ──────────────────────────────────────────────────────

    def assess_gaps(
        self,
        dream_career: str,
        user_skills: list[dict],
        required_skills: list,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns readiness_score, strengths, skill_gaps, quick_wins, etc.

        user_skills     — list of {skill_name, proficiency_level} dicts from DB
        required_skills — list of {skill, category, priority} dicts from career analysis
        """
        user_names = [
            s.get("skill_name", s.get("name", "")) for s in user_skills
        ]
        req_names = [
            (s.get("skill", s) if isinstance(s, dict) else s)
            for s in required_skills
        ]

        prompt = SKILL_GAP_PROMPT.format(
            dream_career=dream_career,
            user_skills=json.dumps(user_names),
            required_skills=json.dumps(req_names),
        )
        return self._call_and_parse(prompt, user_id=user_id, action="assess_gaps")

    # ── Self-assessment questions ──────────────────────────────────────────────

    def generate_questions(
        self,
        career: str,
        skill_area: str,
        user_id: int | None = None,
    ) -> list[dict]:
        """
        Returns 5 self-rating questions (1–5) for a given skill area.
        """
        prompt = (
            f"Generate 5 practical self-assessment questions for someone evaluating "
            f"their {skill_area} skills for a {career} career. "
            f"Make them easy to self-rate on a 1–5 scale.\n\n"
            f"Return a JSON array:\n"
            f'[{{"question":"...", "skill_area":"{skill_area}", "type":"self_rate_1_5"}}]'
        )
        result = self._call_and_parse(
            prompt, user_id=user_id, action="generate_questions"
        )
        return result if isinstance(result, list) else result.get("questions", [])
