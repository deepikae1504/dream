"""
agents/learning_coach.py
Learning Coach Agent — recommends courses, projects, communities.
"""
import json
from agents.base_agent import BaseAgent
from config.prompts import LEARNING_COACH_SYSTEM, RESOURCES_PROMPT


class LearningCoachAgent(BaseAgent):
    name = "Learning Coach Agent"
    system_prompt = LEARNING_COACH_SYSTEM

    def recommend_resources(
        self,
        skill_gap: dict,
        dream_career: str,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns learning_path (per skill), daily_learning_plan,
        free_resources_summary, youtube_channels, communities_to_join.
        """
        top_gaps = skill_gap.get("skill_gaps", [])[:6]

        prompt = RESOURCES_PROMPT.format(
            dream_career=dream_career,
            top_gaps=json.dumps(top_gaps),
        )
        return self._call_and_parse(
            prompt, user_id=user_id, action="recommend_resources"
        )

    def get_project_ideas(
        self,
        skill: str,
        career: str,
        difficulty: str = "Intermediate",
        user_id: int | None = None,
    ) -> list[dict]:
        """Return 3 portfolio-worthy project ideas for a specific skill."""
        prompt = (
            f"Suggest 3 portfolio-worthy project ideas that demonstrate {skill} "
            f"for a {career} role. Difficulty: {difficulty}.\n\n"
            f"Return JSON array:\n"
            f'[{{"title":"...", "description":"...", "tech_stack":["..."], '
            f'"difficulty":"{difficulty}", "github_worthy":true}}]'
        )
        result = self._call_and_parse(
            prompt, user_id=user_id, action="get_project_ideas"
        )
        return result if isinstance(result, list) else []
