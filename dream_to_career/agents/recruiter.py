"""
agents/recruiter.py
Recruiter Perspective Agent — evaluates the user's profile as a real recruiter.
"""
from agents.base_agent import BaseAgent
from config.prompts import RECRUITER_SYSTEM, RECRUITER_PROMPT


class RecruiterAgent(BaseAgent):
    name = "Recruiter Perspective"
    system_prompt = RECRUITER_SYSTEM

    def evaluate_profile(
        self,
        user_profile: dict,
        skills: list[dict],
        interviews: list[dict],
        user_id: int | None = None,
    ) -> dict:
        """
        Returns hiring_probability, first_impression, profile_grade,
        strengths_as_recruiter_sees, red_flags, missing_for_shortlisting,
        resume_advice, interview_readiness, expected_salary_offer,
        time_to_hireable, recruiter_verdict, top_action.
        """
        skill_names = [s.get("skill_name", "") for s in skills]
        avg_interview = (
            sum(i.get("overall_score", 0) for i in interviews) / len(interviews)
            if interviews else 0.0
        )

        prompt = RECRUITER_PROMPT.format(
            dream_career=user_profile.get("dream_career", "Tech role"),
            current_role=user_profile.get("current_role", "Fresher"),
            experience_years=user_profile.get("experience_years", 0),
            education=user_profile.get("education", "Not specified"),
            skills=skill_names,
            interview_avg=avg_interview,
        )
        return self._call_and_parse(
            prompt, user_id=user_id, action="evaluate_profile"
        )
