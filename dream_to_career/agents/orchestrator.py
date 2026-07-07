"""
agents/orchestrator.py
Orchestrator — coordinates all agents for the full onboarding pipeline
and provides a single façade the UI can call.
"""
from __future__ import annotations
import json
from database import db
from agents.career_analyst  import CareerAnalystAgent
from agents.skill_gap        import SkillGapAgent
from agents.roadmap_planner  import RoadmapPlannerAgent
from agents.learning_coach   import LearningCoachAgent
from agents.interview_mentor import InterviewMentorAgent
from agents.accountability   import AccountabilityAgent
from agents.career_twin      import CareerTwinAgent
from agents.whatif_agent     import WhatIfAgent
from agents.recruiter        import RecruiterAgent


class Orchestrator:
    """
    Single entry-point for multi-agent workflows.

    Usage
    -----
    orch = Orchestrator()
    result = orch.run_full_analysis(user_id, dream_career, user_profile, user_skills)
    """

    def __init__(self):
        self.analyst     = CareerAnalystAgent()
        self.skill_gap   = SkillGapAgent()
        self.planner     = RoadmapPlannerAgent()
        self.coach       = LearningCoachAgent()
        self.interviewer = InterviewMentorAgent()
        self.accountable = AccountabilityAgent()
        self.twin        = CareerTwinAgent()
        self.whatif      = WhatIfAgent()
        self.recruiter   = RecruiterAgent()

    # ── Full onboarding pipeline ───────────────────────────────────────────────

    def run_full_analysis(
        self,
        user_id: int,
        dream_career: str,
        user_profile: dict,
        user_skills: list[dict],
        daily_hours: int = 2,
        yield_steps: bool = False,
    ) -> dict:
        """
        Runs: Career Analysis → Skill Gap → Roadmap → Resources
        Returns a single dict with all results.

        If yield_steps=True this is a generator that yields (step_name, partial_result).
        """
        results: dict = {}

        # Step 1 — Career Analysis
        career_result = self.analyst.analyze(dream_career, user_profile, user_id)
        results["career_analysis"] = career_result
        goal_id = db.save_career_goal(
            user_id, dream_career,
            career_report=json.dumps(career_result),
            required_skills=json.dumps(career_result.get("required_skills", [])),
            market_demand=career_result.get("market_demand", ""),
        )
        results["goal_id"] = goal_id
        if yield_steps:
            yield "career_analysis", results.copy()

        # Step 2 — Skill Gap
        required_skills = career_result.get("required_skills", [])
        gap_result = self.skill_gap.assess_gaps(
            dream_career, user_skills, required_skills, user_id
        )
        results["skill_gap"] = gap_result
        if yield_steps:
            yield "skill_gap", results.copy()

        # Step 3 — Roadmap
        roadmap = self.planner.create_roadmap(
            dream_career, gap_result, user_profile, daily_hours, user_id
        )
        results["roadmap"] = roadmap
        db.save_roadmap(
            user_id, goal_id,
            json.dumps(roadmap.get("plan_30_day", {})),
            json.dumps(roadmap.get("plan_90_day", {})),
            json.dumps(roadmap.get("plan_6_month", {})),
            json.dumps(roadmap.get("plan_1_year", {})),
            roadmap.get("key_milestones", []),
        )
        if yield_steps:
            yield "roadmap", results.copy()

        # Step 4 — Resources
        resources = self.coach.recommend_resources(gap_result, dream_career, user_id)
        results["resources"] = resources
        flat = [
            {
                "skill":    path.get("skill", ""),
                "type":     r.get("type", "course"),
                "title":    r.get("title", ""),
                "url":      r.get("url", ""),
                "platform": r.get("platform", ""),
                "free":     r.get("free", True),
                "priority": path.get("priority", 1),
            }
            for path in resources.get("learning_path", [])
            for r in path.get("resources", [])
        ]
        db.save_resources(user_id, flat)
        if yield_steps:
            yield "resources", results.copy()

        return results

    # ── Quick health check (called weekly) ────────────────────────────────────

    def run_weekly_health_check(
        self, user_id: int, user_profile: dict
    ) -> dict:
        """Accountability + Career Twin combined health snapshot."""
        progress   = db.get_progress(user_id, 30)
        interviews = db.get_interviews(user_id, 10)
        skills     = db.get_skills(user_id)

        int_scores = [i.get("overall_score", 0) for i in interviews]
        health = self.accountable.calculate_health_score(
            progress, int_scores, user_profile, user_id
        )
        db.save_health_score(
            user_id,
            health.get("learning_consistency", 0),
            health.get("skill_development", 0),
            health.get("project_building", 0),
            health.get("interview_readiness", 0),
            health.get("overall_score", 0),
            json.dumps(health.get("insights", [])),
        )

        roadmap = db.get_latest_roadmap(user_id)
        plan = {}
        if roadmap:
            try:
                plan = json.loads(roadmap.get("plan_30_day", "{}") or "{}")
            except Exception:
                pass

        weekly_plan = self.accountable.generate_weekly_plan(
            health, {"plan_30_day": plan}, user_profile, user_id
        )

        twin = self.twin.predict_future(
            user_profile, skills, progress, health, user_id
        )

        return {
            "health_score": health,
            "weekly_plan":  weekly_plan,
            "career_twin":  twin,
        }

    # ── What-if shortcut ───────────────────────────────────────────────────────

    def run_whatif(
        self,
        scenario: str,
        user_id: int,
        user_profile: dict,
    ) -> dict:
        health_scores = db.get_health_scores(user_id, 1)
        health = health_scores[0] if health_scores else {}
        result = self.whatif.simulate(scenario, user_profile, health, user_id)
        db.save_whatif(
            user_id, scenario, {},
            result.get("long_term_impact", ""),
            result.get("timeline_change", ""),
            result.get("new_success_probability", 50),
            result.get("verdict_reason", ""),
        )
        return result
