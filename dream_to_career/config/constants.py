"""
config/constants.py
All hard-coded look-up values, palette, and domain data used across the app.
"""

# ── Brand palette ──────────────────────────────────────────────────────────────
COLORS = {
    "primary":   "#6C63FF",
    "secondary": "#00D4AA",
    "accent":    "#FF6584",
    "warning":   "#FFB84D",
    "bg_dark":   "#0D0F1C",
    "bg_card":   "#161929",
    "bg_hover":  "#1E2235",
    "text_main": "#E8E9F3",
    "text_muted":"#8890B5",
}

# ── Skill taxonomy ─────────────────────────────────────────────────────────────
SKILL_CATEGORIES = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "R", "SQL",
    ],
    "AI / ML": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Reinforcement Learning", "TensorFlow", "PyTorch", "Scikit-learn",
        "Hugging Face", "LangChain",
    ],
    "Web Development": [
        "React", "Next.js", "Node.js", "FastAPI", "Django", "Flask",
        "HTML/CSS", "REST APIs", "GraphQL", "WebSockets",
    ],
    "Data Engineering": [
        "Pandas", "NumPy", "Spark", "Kafka", "Airflow",
        "Data Pipelines", "ETL", "dbt", "BigQuery", "Snowflake",
    ],
    "Cloud & DevOps": [
        "AWS", "GCP", "Azure", "Docker", "Kubernetes",
        "CI/CD", "Terraform", "Linux", "Git", "GitHub Actions",
    ],
    "Data Visualization": [
        "Tableau", "Power BI", "Plotly", "Matplotlib", "Seaborn", "D3.js",
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQLite",
    ],
    "Soft Skills": [
        "Communication", "Problem Solving", "Critical Thinking",
        "Time Management", "Leadership", "Teamwork", "Public Speaking",
    ],
}

# ── Career presets ─────────────────────────────────────────────────────────────
POPULAR_CAREERS = [
    "AI / ML Engineer",
    "Data Scientist",
    "Full Stack Web Developer",
    "Backend Engineer",
    "Frontend Engineer",
    "Cloud Solutions Architect",
    "DevOps / SRE Engineer",
    "Cybersecurity Analyst",
    "Product Manager (Tech)",
    "Data Analyst",
    "Blockchain Developer",
    "iOS / Android Developer",
    "Game Developer",
    "Embedded Systems Engineer",
    "Quantum Computing Researcher",
]

# ── Proficiency labels ─────────────────────────────────────────────────────────
PROFICIENCY_LABELS = {
    0: "Not known",
    1: "Beginner",
    2: "Elementary",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert",
}

# ── Interview types ────────────────────────────────────────────────────────────
INTERVIEW_TYPES = [
    "Technical",
    "HR / Behavioral",
    "System Design",
    "Case Study",
    "Mixed",
]

INTERVIEW_DIFFICULTY = ["Easy", "Mixed", "Hard"]

# ── Activity types (for progress logging) ────────────────────────────────────
ACTIVITY_TYPES = [
    "Watching course",
    "Reading documentation",
    "Building project",
    "Practice problems / LeetCode",
    "Mock interview",
    "Code review",
    "Writing notes / summary",
    "Attending workshop / bootcamp",
    "Contributing to open source",
    "Networking / LinkedIn",
    "Other",
]

# ── What-If preset scenarios ───────────────────────────────────────────────────
WHATIF_PRESETS = [
    "What if I study 4 hours daily instead of 2?",
    "What if I skip Data Structures & Algorithms entirely?",
    "What if I focus only on AI/ML and ignore web development?",
    "What if I start applying for jobs right now?",
    "What if I build real projects before finishing courses?",
    "What if I get certified first before building projects?",
    "What if I join a bootcamp instead of self-learning?",
    "What if I take a 2-month break?",
    "What if I switch my target from Software Engineer to Data Analyst?",
    "What if I contribute to open-source from day 1?",
    "What if I spend 50% of my time on networking and LinkedIn?",
    "What if I focus on freelancing before applying to full-time jobs?",
]

# ── Education levels ───────────────────────────────────────────────────────────
EDUCATION_LEVELS = [
    "High School / 12th",
    "Diploma",
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Self-taught / Bootcamp",
    "Currently Studying",
]

# ── Priority color map ─────────────────────────────────────────────────────────
PRIORITY_COLORS = {
    "Critical": COLORS["accent"],
    "High":     COLORS["warning"],
    "Medium":   COLORS["primary"],
    "Low":      COLORS["text_muted"],
}

# ── Platform icons ─────────────────────────────────────────────────────────────
PLATFORM_ICONS = {
    "youtube":          "▶️",
    "coursera":         "🎓",
    "freecodecamp":     "💻",
    "udemy":            "🎯",
    "edx":              "🏫",
    "fast.ai":          "⚡",
    "kaggle":           "📊",
    "github":           "🐙",
    "docs":             "📖",
    "documentation":    "📖",
    "google":           "🔵",
    "stanford":         "🌲",
    "harvard":          "🔴",
    "mit":              "⚙️",
    "linkedin":         "💼",
    "pluralsight":      "🟣",
    "datacamp":         "📈",
    "codecademy":       "🟠",
    "default":          "📌",
}

# ── Health score thresholds ────────────────────────────────────────────────────
HEALTH_THRESHOLDS = {
    "excellent": 80,
    "good":      60,
    "average":   40,
    "poor":       0,
}

HEALTH_LABELS = {
    "excellent": ("A", COLORS["secondary"]),
    "good":      ("B", COLORS["primary"]),
    "average":   ("C", COLORS["warning"]),
    "poor":      ("D", COLORS["accent"]),
}

# ── Agent names ────────────────────────────────────────────────────────────────
AGENT_NAMES = {
    "career_analyst":   "Career Analyst Agent",
    "skill_gap":        "Skill Gap Agent",
    "roadmap_planner":  "Roadmap Planner Agent",
    "learning_coach":   "Learning Coach Agent",
    "interview_mentor": "Interview Mentor Agent",
    "accountability":   "Accountability Agent",
    "career_twin":      "AI Career Twin",
    "whatif":           "What-If Simulator",
    "recruiter":        "Recruiter Perspective",
    "orchestrator":     "Orchestrator",
}
