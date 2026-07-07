"""
config/prompts.py
Centralised prompt templates for every agent.
Keep all LLM-facing text here so it's easy to iterate without touching agent logic.
"""

# ── System prompts ─────────────────────────────────────────────────────────────

CAREER_ANALYST_SYSTEM = """You are an expert career analyst with deep knowledge of industry
trends, job markets, career paths, and compensation data across the tech industry.
You specialise in the Indian and global job markets.
Rules:
- Be specific and data-driven (use realistic INR salary ranges for India).
- Always be encouraging while staying honest.
- Prioritise actionable insights over generic advice.
- Return ONLY valid JSON when asked for structured output."""

SKILL_GAP_SYSTEM = """You are a precise skill-gap assessment specialist.
You objectively measure the distance between a learner's current skills and their
target career requirements, then create prioritised development plans.
Rules:
- Score readiness from 0–100 based on genuine evidence, not flattery.
- Prioritise gaps by career impact, not difficulty.
- Surface 'quick wins' — skills learnable in < 2 weeks that boost employability fast.
- Return ONLY valid JSON when asked for structured output."""

ROADMAP_PLANNER_SYSTEM = """You are a strategic career roadmap architect.
You create detailed, realistic, milestone-driven learning plans tailored to a
learner's starting point, available hours, and target career.
Rules:
- Build in buffer time; most people study less than they plan.
- Every phase must have a concrete, measurable milestone.
- Suggest real projects that can go on a GitHub portfolio.
- Return ONLY valid JSON when asked for structured output."""

LEARNING_COACH_SYSTEM = """You are an experienced learning coach who recommends the
best free and paid resources for tech careers.
You prioritise practical, project-based learning over passive consumption.
Rules:
- Prefer free resources where possible; always flag paid ones clearly.
- Recommend resources you are confident exist (Coursera, YouTube, fast.ai, etc.).
- Include hands-on projects for every skill area.
- Return ONLY valid JSON when asked for structured output."""

INTERVIEW_MENTOR_SYSTEM = """You are a senior technical interviewer and career coach
with 10+ years at top tech companies (Google, Microsoft, Amazon, startups).
You give fair, detailed, growth-oriented feedback after mock interviews.
Rules:
- Score answers 1–10 with clear criteria.
- Highlight both strengths and concrete improvements.
- Give 'ideal answer hints' — key points the candidate missed.
- Return ONLY valid JSON when asked for structured output."""

ACCOUNTABILITY_SYSTEM = """You are a supportive but firm accountability coach.
You celebrate wins, identify warning patterns early, and keep learners motivated
through data-driven weekly health scores.
Rules:
- Be honest about low scores — false encouragement helps no one.
- Always end with an actionable focus task for the coming week.
- Return ONLY valid JSON when asked for structured output."""

CAREER_TWIN_SYSTEM = """You are an AI career simulation engine that creates predictive
'career twin' models for learners.
You combine activity data, skill levels, and trajectory analysis to forecast realistic
future outcomes with probability estimates.
Rules:
- Base predictions on actual input data, not wishful thinking.
- Identify specific risks with concrete mitigation actions.
- The 'twin message' should feel personal and motivating.
- Return ONLY valid JSON when asked for structured output."""

WHATIF_SYSTEM = """You are a career simulation engine that models the impact of
different learning choices on a person's career trajectory.
Rules:
- Be honest — some choices genuinely hurt outcomes.
- Quantify impact where possible (timeline change, probability shift).
- Always offer a better alternative when verdict is 'Not Recommended'.
- Return ONLY valid JSON when asked for structured output."""

RECRUITER_SYSTEM = """You are a senior tech recruiter who has screened 10 000+ profiles
for engineering roles at top companies.
You give brutally honest, constructive profile evaluations.
Rules:
- Use realistic hiring-probability percentages based on the evidence given.
- Identify red flags a real recruiter would notice immediately.
- Salary estimates should reflect current Indian market rates.
- Return ONLY valid JSON when asked for structured output."""


# ── Prompt templates (call .format(**kwargs)) ──────────────────────────────────

CAREER_ANALYSIS_PROMPT = """
Analyse the career path for: {dream_career}

User profile:
- Current role     : {current_role}
- Years experience : {experience_years}
- Education        : {education}

Return a JSON object with EXACTLY these keys:
{{
  "career_title": "...",
  "overview": "2-3 sentence summary",
  "market_demand": "High | Medium | Low — one-line reason",
  "avg_salary_range": "₹X LPA – ₹Y LPA",
  "required_skills": [
    {{"skill":"...", "category":"Technical|Soft|Domain",
      "priority":"Must Have|Good to Have", "level":"Beginner|Intermediate|Advanced"}}
  ],
  "career_stages": [
    {{"stage":"...", "timeline":"...", "typical_roles":["..."], "salary":"₹X–₹Y LPA"}}
  ],
  "top_companies": ["..."],
  "growth_outlook": "...",
  "key_certifications": ["..."],
  "daily_work": "What a typical workday looks like",
  "success_factors": ["..."],
  "challenges": ["..."]
}}
"""

SKILL_GAP_PROMPT = """
Assess the skill gap for a learner targeting: {dream_career}

Skills the learner ALREADY HAS: {user_skills}
Skills REQUIRED for the career : {required_skills}

Return JSON with EXACTLY these keys:
{{
  "readiness_score": <integer 0-100>,
  "readiness_level": "Beginner|Intermediate|Advanced",
  "strengths": [{{"skill":"...", "note":"..."}}],
  "skill_gaps": [
    {{"skill":"...", "priority":"Critical|High|Medium|Low",
      "effort_weeks":<int>, "category":"..."}}
  ],
  "immediate_focus": ["top 3 skills to start NOW"],
  "gap_summary": "2-3 sentence honest summary",
  "estimated_readiness_timeline_months": <int>,
  "quick_wins": ["skills learnable in under 2 weeks"]
}}
"""

ROADMAP_PROMPT = """
Create a personalised career roadmap for: {dream_career}

Context:
- Starting point  : {current_role}
- Daily study hrs : {daily_hours}
- Readiness score : {readiness_score}%
- Top skill gaps  : {top_gaps}

Return JSON with EXACTLY these keys:
{{
  "roadmap_title": "...",
  "total_duration_months": <int>,
  "plan_30_day":  {{"theme":"...", "goals":["..."], "daily_tasks":["..."],
                    "milestone":"...", "key_resources":["..."]}},
  "plan_90_day":  {{"theme":"...", "goals":["..."], "projects_to_build":["..."],
                    "milestone":"...", "key_resources":["..."]}},
  "plan_6_month": {{"theme":"...", "goals":["..."], "portfolio_items":["..."],
                    "milestone":"...", "interview_prep":"Start|Not yet"}},
  "plan_1_year":  {{"theme":"...", "goals":["..."], "expected_outcome":"...",
                    "milestone":"...", "salary_expectation":"₹X–₹Y LPA"}},
  "weekly_schedule": {{
    "monday":"...", "tuesday":"...", "wednesday":"...",
    "thursday":"...", "friday":"...", "weekend":"..."
  }},
  "key_milestones": [
    {{"month":<int>, "milestone":"...", "metric":"..."}}
  ]
}}
"""

RESOURCES_PROMPT = """
Recommend learning resources for: {dream_career}
Top skill gaps: {top_gaps}

Return JSON with EXACTLY these keys:
{{
  "learning_path": [
    {{
      "skill": "...",
      "priority": <int 1-based>,
      "resources": [
        {{"title":"...", "platform":"...", "url":"https://...",
          "type":"course|video|docs|book",
          "duration":"...", "free":<bool>,
          "rating":<float>, "why_recommended":"..."}}
      ],
      "projects": [
        {{"title":"...", "description":"...", "difficulty":"Beginner|Intermediate|Advanced"}}
      ]
    }}
  ],
  "daily_learning_plan": {{
    "morning":"15-min habit",
    "main_session":"core focus",
    "evening":"review / practice"
  }},
  "free_resources_summary": ["top 3 free picks overall"],
  "youtube_channels": ["channel name"],
  "communities_to_join": ["community (platform)"]
}}
"""

INTERVIEW_QUESTIONS_PROMPT = """
Generate {num_questions} {interview_type} interview questions for a {career} role.
Difficulty mix: {difficulty}

Return a JSON ARRAY only:
[
  {{
    "id": <int>,
    "question": "...",
    "type": "{interview_type}",
    "difficulty": "Easy|Medium|Hard",
    "what_to_look_for": "key points in an ideal answer",
    "follow_up": "optional deeper question"
  }}
]
"""

ANSWER_EVALUATION_PROMPT = """
Evaluate this mock-interview answer for a {career} role.

Question : {question}
Answer   : {answer}

Return JSON:
{{
  "score": <int 1-10>,
  "score_out_of": 10,
  "strengths": ["..."],
  "improvements": ["..."],
  "ideal_answer_hints": ["key points missing"],
  "feedback": "2-3 sentence detailed feedback",
  "verdict": "Strong|Good|Average|Needs Work"
}}
"""

OVERALL_INTERVIEW_PROMPT = """
A candidate for {career} just completed a mock interview.
Individual question scores : {scores}
Average score             : {avg:.1f}/10

Return comprehensive feedback JSON:
{{
  "overall_score": {avg:.1f},
  "performance_level": "Excellent|Good|Average|Needs Improvement",
  "overall_feedback": "3-4 sentence overall assessment",
  "top_strengths": ["..."],
  "critical_improvements": ["..."],
  "next_steps": ["actionable step 1", "step 2", "step 3"],
  "readiness_estimate": "3 months | 6 months | Ready now",
  "encouragement": "Motivational closing (1-2 sentences)"
}}
"""

HEALTH_SCORE_PROMPT = """
Calculate the weekly career health score for this learner.

Activity data (last 14 days):
- Total study hours logged : {total_hours}
- Days with any activity   : {active_days}
- Milestones completed     : {milestones}
- Recent activity types    : {recent_activities}

Interview scores (last 3) : {interview_scores}
Target career             : {dream_career}

Return JSON:
{{
  "learning_consistency": <int 0-100>,
  "skill_development":    <int 0-100>,
  "project_building":     <int 0-100>,
  "interview_readiness":  <int 0-100>,
  "overall_score":        <float 0-100>,
  "grade":  "A|B|C|D",
  "insights": ["observation 1", "observation 2"],
  "this_week_focus": "single top-priority task for next 7 days",
  "motivational_message": "personalised encouragement (2 sentences)",
  "streak_days": <int>,
  "areas_at_risk": ["area needing immediate attention"]
}}
"""

CAREER_TWIN_PROMPT = """
Create an AI Career Twin prediction for this learner.

Profile:
- Dream career     : {dream_career}
- Current role     : {current_role}
- Known skills     : {skills}
- Active days / 30 : {active_days}
- Health score     : {health_score}

Return JSON:
{{
  "twin_name": "e.g. 'Future AI Engineer You'",
  "current_trajectory": "honest 1-sentence assessment",
  "success_probability": <int 0-100>,
  "predicted_timeline": "e.g. '10 months at current pace'",
  "predicted_first_salary": "₹X–₹Y LPA",
  "predicted_3_year_salary": "₹X–₹Y LPA",
  "career_milestones_predicted": [
    {{"milestone":"...", "predicted_month":<int>}}
  ],
  "critical_risks": [
    {{"risk":"...", "probability":"High|Medium|Low", "mitigation":"..."}}
  ],
  "opportunities": [
    {{"opportunity":"...", "action_needed":"..."}}
  ],
  "missing_skills_for_success": ["skill1", "skill2"],
  "competitive_advantage": "what makes this person stand out",
  "twin_message": "message from future self (2-3 sentences, first person)"
}}
"""

WHATIF_PROMPT = """
Simulate this career scenario: "{scenario}"

User context:
- Dream career  : {dream_career}
- Current role  : {current_role}
- Health score  : {health_score}

Return JSON:
{{
  "scenario": "{scenario}",
  "short_term_impact":  "impact in next 30 days",
  "medium_term_impact": "impact in 3-6 months",
  "long_term_impact":   "impact in 1-2 years",
  "success_probability_change": "+X% | -X%",
  "new_success_probability": <int 0-100>,
  "timeline_change": "+X months | -X months | No change",
  "pros": ["..."],
  "cons": ["..."],
  "verdict": "Recommended|Not Recommended|Neutral",
  "verdict_reason": "2-3 sentence explanation",
  "alternative_suggestion": "better approach if verdict is negative (else empty string)",
  "confidence": "High|Medium|Low"
}}
"""

RECRUITER_PROMPT = """
Evaluate this candidate as a recruiter for: {dream_career}

Candidate:
- Current role  : {current_role}
- Experience    : {experience_years} years
- Education     : {education}
- Known skills  : {skills}
- Mock interview avg : {interview_avg:.1f}/10

Return JSON:
{{
  "hiring_probability": <int 0-100>,
  "first_impression": "what you think in the first 30 seconds",
  "profile_grade": "A+|A|B+|B|C+|C|D",
  "strengths_as_recruiter_sees": ["..."],
  "red_flags": ["..."],
  "missing_for_shortlisting": ["what's needed to get shortlisted"],
  "resume_advice": ["resume tip 1", "tip 2"],
  "interview_readiness": "Not ready|Partially ready|Ready",
  "expected_salary_offer": "₹X–₹Y LPA",
  "time_to_hireable": "realistic timeline",
  "recruiter_verdict": "honest 3-4 sentence assessment",
  "top_action": "single most impactful action right now"
}}
"""

WEEKLY_PLAN_PROMPT = """
Create a focused weekly plan based on the learner's current health score.

Health scores : {health_scores}
Roadmap theme : {roadmap_theme}
Dream career  : {dream_career}

Return JSON:
{{
  "week_theme": "...",
  "daily_goals": [
    {{"day":"Monday", "primary_task":"...", "secondary_task":"...", "hours":<float>}},
    {{"day":"Tuesday",  "primary_task":"...", "secondary_task":"...", "hours":<float>}},
    {{"day":"Wednesday","primary_task":"...", "secondary_task":"...", "hours":<float>}},
    {{"day":"Thursday", "primary_task":"...", "secondary_task":"...", "hours":<float>}},
    {{"day":"Friday",   "primary_task":"...", "secondary_task":"...", "hours":<float>}},
    {{"day":"Saturday", "primary_task":"...", "secondary_task":"...", "hours":<float>}},
    {{"day":"Sunday",   "primary_task":"...", "secondary_task":"...", "hours":<float>}}
  ],
  "weekly_challenge": "one stretch goal",
  "accountability_check": "how to verify progress",
  "reward": "small reward for completing the week"
}}
"""
