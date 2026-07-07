"""
agents/whatif_agent.py
What-If Simulator — models the impact of different learning decisions.
"""
from agents.base_agent import BaseAgent
from config.prompts import WHATIF_SYSTEM, WHATIF_PROMPT


class WhatIfAgent(BaseAgent):
    name = "What-If Simulator"
    system_prompt = WHATIF_SYSTEM

    def simulate(
        self,
        scenario: str,
        user_profile: dict,
        health_score: dict | None = None,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns scenario, short/medium/long-term impact,
        success_probability_change, new_success_probability,
        timeline_change, pros, cons, verdict, verdict_reason,
        alternative_suggestion, confidence.
        """
        h_score = health_score.get("overall_score", 50) if health_score else 50

        prompt = WHATIF_PROMPT.format(
            scenario=scenario,
            dream_career=user_profile.get("dream_career", "AI Engineer"),
            current_role=user_profile.get("current_role", "Fresher"),
            health_score=h_score,
        )
        return self._call_and_parse(
            prompt, user_id=user_id, action="simulate"
        )
