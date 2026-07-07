"""
agents/interview_mentor.py
Interview Mentor Agent — mock interviews, answer evaluation, overall scoring.
"""
from agents.base_agent import BaseAgent
from config.prompts import (
    INTERVIEW_MENTOR_SYSTEM,
    INTERVIEW_QUESTIONS_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    OVERALL_INTERVIEW_PROMPT,
)


class InterviewMentorAgent(BaseAgent):
    name = "Interview Mentor Agent"
    system_prompt = INTERVIEW_MENTOR_SYSTEM

    # ── Question generation ────────────────────────────────────────────────────

    def generate_questions(
        self,
        career: str,
        interview_type: str = "Technical",
        difficulty: str = "Mixed",
        num_questions: int = 5,
        user_id: int | None = None,
    ) -> list[dict]:
        """
        Returns a list of question dicts:
        id, question, type, difficulty, what_to_look_for, follow_up.
        """
        prompt = INTERVIEW_QUESTIONS_PROMPT.format(
            num_questions=num_questions,
            interview_type=interview_type,
            career=career,
            difficulty=difficulty,
        )
        result = self._call_and_parse(
            prompt, user_id=user_id, action="generate_questions"
        )
        return result if isinstance(result, list) else []

    # ── Single answer evaluation ───────────────────────────────────────────────

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        career: str,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns score (1-10), strengths, improvements,
        ideal_answer_hints, feedback, verdict.
        """
        prompt = ANSWER_EVALUATION_PROMPT.format(
            career=career,
            question=question,
            answer=answer,
        )
        return self._call_and_parse(
            prompt, user_id=user_id, action="evaluate_answer"
        )

    # ── Final overall feedback ─────────────────────────────────────────────────

    def generate_overall_feedback(
        self,
        scores: list[float],
        career: str,
        user_id: int | None = None,
    ) -> dict:
        """
        Returns overall_score, performance_level, overall_feedback,
        top_strengths, critical_improvements, next_steps,
        readiness_estimate, encouragement.
        """
        avg = sum(scores) / len(scores) if scores else 0.0
        prompt = OVERALL_INTERVIEW_PROMPT.format(
            career=career,
            scores=scores,
            avg=avg,
        )
        return self._call_and_parse(
            prompt, user_id=user_id, action="overall_feedback"
        )
