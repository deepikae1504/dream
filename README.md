# 🚀 Dream-to-Career AI

> **9 AI agents turn your dream job into a step-by-step plan — with skill gaps, mock interviews, a career twin, and weekly scores to keep you on track.**

Built with **Google Gemini · Python · Streamlit · SQLite**  
Free to run · Open source · Runs entirely on your machine

---

## Table of Contents

- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Live Demo Flow](#live-demo-flow)
- [Agent Architecture](#agent-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Contributing](#contributing)

---

## The Problem

Breaking into a new tech career is hard — not because the information isn't out there, but because **generic advice doesn't work for individuals**.

| Pain Point | Reality |
|---|---|
| "Learn Python, ML, and Docker" | Everyone gets the same list regardless of their background |
| Career roadmap blogs | Written for the average person — not for *you* |
| No accountability | Most learners drop off within 3 weeks without a system |
| No feedback loop | You don't know if you're actually making progress |
| Interview prep | Expensive coaching or ineffective solo grinding |

A 22-year-old CS fresher and a 35-year-old backend engineer pivoting into ML have completely different gaps, timelines, and priorities. They should not be reading the same roadmap.

---

## The Solution

**Dream-to-Career AI** deploys a coordinated team of 9 specialized AI agents that analyze your specific situation and produce a deeply personalized career plan.

```
You say:  "I want to become an AI Engineer"

The system does:
  ┌─────────────────────────────────────────────────────────┐
  │  Career Analyst  →  What does the market actually need? │
  │  Skill Gap Agent →  How far are YOU from that target?   │
  │  Roadmap Planner →  What's YOUR step-by-step plan?      │
  │  Learning Coach  →  What should YOU learn first?        │
  │  Interview Mentor → How do YOU perform in interviews?   │
  │  Accountability  →  Are YOU actually making progress?   │
  │  Career Twin     →  Where is YOUR trajectory heading?   │
  │  What-If Sim     →  What if YOU change your strategy?   │
  │  Recruiter View  →  How does a recruiter see YOU?       │
  └─────────────────────────────────────────────────────────┘

You get: A personalized, trackable, AI-powered career journey
```

---

## Live Demo Flow

```
1. Enter dream career  →  "AI/ML Engineer at Google"
          │
          ▼
2. Career Analysis     →  Salary ₹8–35 LPA · 18 skills required · High demand
          │
          ▼
3. Skill Assessment    →  Readiness: 42% · 11 gaps found · 3 quick wins
          │
          ▼
4. Roadmap Generated   →  30-day: Python+ML basics
                          90-day: Build 2 projects
                          6-month: Portfolio + apply
                          1-year: Land first role
          │
          ▼
5. Learning Hub        →  fast.ai (free) · Kaggle Learn · Andrew Ng's course
          │
          ▼
6. Mock Interview      →  Score: 6.8/10 · Needs work on system design
          │
          ▼
7. Progress Dashboard  →  Health Score: 68/100 · Grade: B+ · 5-day streak
          │
          ▼
8. Career Twin         →  74% success probability · First job: Month 9
                          Predicted salary: ₹8–12 LPA → ₹18–28 LPA (3yr)
          │
          ▼
9. What-If Simulator   →  "Study 4hrs/day?" → +12%, -3 months ✅
                          "Skip DSA?" → -18%, +4 months ❌
```

---

## Agent Architecture

```
                    ┌─────────────────────┐
                    │     User Input      │
                    │ "I want to be an    │
                    │  AI Engineer"       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Orchestrator     │
                    │  Coordinates all   │
                    │  agent pipelines   │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
┌─────────▼────────┐ ┌─────────▼────────┐ ┌────────▼─────────┐
│  Career Analyst  │ │  Skill Gap Agent  │ │ Roadmap Planner  │
│                  │ │                  │ │                  │
│ • Market demand  │ │ • Readiness score│ │ • 30-day plan    │
│ • Salary ranges  │ │ • Gap matrix     │ │ • 90-day plan    │
│ • Required skills│ │ • Quick wins     │ │ • 6-month plan   │
│ • Career stages  │ │ • Priority order │ │ • 1-year plan    │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
┌─────────▼────────┐ ┌─────────▼────────┐ ┌────────▼─────────┐
│ Learning Coach   │ │Interview Mentor  │ │ Accountability   │
│                  │ │                  │ │                  │
│ • Free courses   │ │ • Mock questions │ │ • Health score   │
│ • YouTube picks  │ │ • Answer scoring │ │ • Weekly plan    │
│ • Project ideas  │ │ • Full feedback  │ │ • Motivational   │
│ • Daily routine  │ │ • Readiness est. │ │   nudges         │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
┌─────────▼────────┐ ┌─────────▼────────┐ ┌────────▼─────────┐
│  AI Career Twin  │ │ What-If Simulator│ │ Recruiter View   │
│                  │ │                  │ │                  │
│ • Future pred.   │ │ • Scenario model │ │ • Hire probab.   │
│ • Success prob.  │ │ • Impact on time │ │ • Profile grade  │
│ • Salary forcast │ │ • Pros and cons  │ │ • Red flags      │
│ • Risks + opps   │ │ • Verdict        │ │ • Top action     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Personalized      │
                    │   Career Journey    │
                    │   Ready ✅          │
                    └─────────────────────┘
```

### How Agents Communicate

Every agent:
1. Reads user profile + context from **SQLite**
2. Calls **Gemini API** with a structured prompt from `config/prompts.py`
3. Parses JSON response via `BaseAgent._call_and_parse()`
4. Writes results back to **SQLite**
5. Logs execution time + status to `agent_logs` table

The **Orchestrator** chains agents in sequence for the onboarding pipeline and provides shortcuts for individual agent calls throughout the app.

---

## Features

### 🔭 Career Analysis
- Deep market research on any tech role
- Salary benchmarks for India (LPA ranges by career stage)
- Required skills ranked by priority
- Top hiring companies
- 5-year growth outlook
- What a typical workday looks like

### 🧩 Skill Gap Assessment
- Self-rate 60+ skills across 8 categories
- AI-powered gap analysis vs. role requirements
- Readiness score 0–100
- Instant local estimate (no API call needed)
- Gap matrix with weeks-to-learn estimates
- Quick wins: skills learnable in under 2 weeks

### 🗺️ Personalized Roadmap
- Calibrated to your daily study hours (1–8 hrs)
- 30-day foundation → 90-day core → 6-month portfolio → 1-year hired
- Concrete milestones with measurable outcomes
- Day-by-day weekly schedule
- Downloadable as Markdown

### 📚 Learning Hub
- AI-curated courses per skill gap
- Strong bias toward free resources
- YouTube channels to follow
- Communities to join
- Hands-on project ideas for portfolio
- Progress logging with streak tracking

### 🎤 Mock Interviews
- Technical, behavioral, system design, case study, or mixed
- Easy / Medium / Hard difficulty
- Per-answer scoring (1–10) with strengths + improvements
- Comprehensive post-session report
- Interview history with score tracking

### 📊 Weekly Health Score
- Four dimensions: Learning · Skills · Projects · Interviews
- Letter grade (A–D)
- Personalized motivational message
- Weekly study plan with daily goals
- Activity log with CSV export

### 🤖 AI Career Twin
- Success probability percentage
- Predicted career milestones with month estimates
- Salary forecast: first job and 3-year projection
- Critical risks with mitigation strategies
- Opportunities you're currently missing
- Message from your future self

### ⚡ What-If Simulator
- 12 preset scenarios (skip DSA, study 4hrs/day, etc.)
- Custom scenario input
- Probability change + timeline impact
- Pros, cons, verdict, and better alternative
- Side-by-side scenario comparison chart

### 👔 Recruiter Perspective
- Hiring probability percentage
- Profile grade (A+ to D)
- Red flags a real recruiter would notice
- Expected salary offer range
- Realistic time to hireability
- Single most impactful action to take now

### 🔬 Analytics & Observability
- Full agent execution log with timing
- Input/output traces per agent call
- Raw data inspector for all 10 DB tables
- Profile JSON export
- Activity CSV export

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| AI | Google Gemini (`gemini-2.0-flash-lite`) | All agent reasoning and generation |
| Backend | Python 3.10+ | Application logic |
| Frontend | Streamlit | Web UI (10 pages) |
| Database | SQLite | Local data persistence |
| Charts | Plotly | Gauges, radar, line, bar charts |
| Data | Pandas | Progress log processing |

---

## Project Structure

```
dream_to_career/
│
├── app.py                        # Entry point — Home page + sidebar
│
├── config/
│   ├── constants.py              # Skills, careers, colors, presets
│   ├── settings.py               # Model, retries, paths, feature flags
│   └── prompts.py                # All 15 agent prompt templates
│
├── agents/
│   ├── base_agent.py             # BaseAgent: Gemini calls, retry, logging
│   ├── career_analyst.py         # Career market intelligence
│   ├── skill_gap.py              # Gap analysis and readiness scoring
│   ├── roadmap_planner.py        # 30-day to 1-year plan generation
│   ├── learning_coach.py         # Resource and project recommendations
│   ├── interview_mentor.py       # Question gen, answer eval, feedback
│   ├── accountability.py         # Health scores and weekly plans
│   ├── career_twin.py            # Trajectory prediction
│   ├── whatif_agent.py           # Scenario simulation
│   ├── recruiter.py              # Profile evaluation as recruiter
│   └── orchestrator.py           # Multi-agent pipeline coordinator
│
├── database/
│   └── db.py                     # SQLite schema, init, and all CRUD helpers
│
├── tools/
│   ├── career_tools.py           # Progress summary, streak, health grade
│   ├── assessment_tools.py       # Local readiness score, gap matrix, radar data
│   └── simulation_tools.py       # Probability model, salary projection, scenario delta
│
├── utils/
│   ├── ui_components.py          # Shared CSS, page_header, metric_card, charts
│   ├── charts.py                 # All Plotly chart builders
│   ├── session.py                # st.session_state manager
│   ├── sidebar.py                # Shared sidebar (API key, model, nav)
│   ├── validators.py             # Input validation helpers
│   ├── exporters.py              # Markdown, CSV, JSON export generators
│   └── gemini_client.py          # Standalone Gemini SDK wrapper
│
├── pages/
│   ├── 01_Home.py                # Onboarding form
│   ├── 02_Career_Analysis.py     # Career Analyst Agent UI
│   ├── 03_Skill_Assessment.py    # Skill Gap Agent UI
│   ├── 04_Roadmap_Generator.py   # Roadmap Planner Agent UI
│   ├── 05_Learning_Hub.py        # Learning Coach Agent UI
│   ├── 06_AI_Career_Twin.py      # Career Twin + Recruiter UI
│   ├── 07_WhatIf_Simulator.py    # What-If Simulator UI
│   ├── 08_Mock_Interview.py      # Interview Mentor UI
│   ├── 09_Progress_Dashboard.py  # Accountability Agent UI
│   └── 10_Analytics.py           # Observability + Admin UI
│
├── requirements.txt
├── .env.example                  # API key template
├── .streamlit/
│   └── secrets.toml              # Alternative key storage
└── fix_filenames.py              # Windows emoji filename repair utility
```

---

## Database Schema

```sql
-- 10 tables covering the full user journey

users                    -- Profile, experience, dream career
skills                   -- Self-rated skills with proficiency levels
career_goals             -- Active and archived career targets
roadmaps                 -- Generated 30-day / 90-day / 6-month / 1-year plans
learning_resources       -- Curated course and project recommendations
progress_tracking        -- Daily activity logs with hours and milestones
interviews               -- Mock interview sessions with scores and feedback
career_twin_predictions  -- AI Career Twin trajectory simulations
whatif_simulations       -- What-If Simulator scenario results
career_health_scores     -- Weekly health scores across 4 dimensions
agent_logs               -- Execution log for every Gemini API call
conversation_history     -- Per-agent conversation memory
```

All data is stored locally in `dream_career.db` — nothing is sent to any server except the prompts you send to the Gemini API.

---

## Setup & Installation

### Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.10 or higher | `python --version` |
| pip | Latest | `pip --version` |
| Gemini API key | Free tier | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

### Step 1 — Download the project

Download and extract the zip, or clone the repository:

```bash
# Option A: Extract the downloaded zip
# Extract dream-to-career-ai.zip to your preferred location

# Option B: Clone from GitHub
git clone https://github.com/yourusername/dream-to-career-ai.git
```

### Step 2 — Navigate to the project folder

```bash
cd dream_to_career
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` — web UI framework
- `google-genai` — Gemini API SDK
- `plotly` — charts and visualizations
- `pandas` — data processing
- `python-dotenv` — `.env` file loading

### Step 4 — Add your Gemini API key

**Option A — `.env` file (recommended):**

```bash
# Copy the template
copy .env.example .env          # Windows
cp .env.example .env            # Mac/Linux

# Open .env and replace the placeholder with your real key
# GEMINI_API_KEY=AIzaSyYOUR_ACTUAL_KEY_HERE
```

**Option B — App sidebar (easiest):**

Skip this step and paste your key in the app sidebar after launch.

**Option C — Streamlit secrets:**

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "AIzaSyYOUR_ACTUAL_KEY_HERE"
```

### Step 5 — Run the app

```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

---

## Configuration

### Getting a Free Gemini API Key

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API key"** → **"Create API key in new project"**
4. Copy the key (starts with `AIza...`)

### Choosing a Model

Select your model in the sidebar under **🤖 Model**:

| Model | Free Quota | Best For |
|---|---|---|
| `gemini-2.0-flash-lite` | Highest (default) | Daily use, all features |
| `gemini-2.0-flash` | Medium | Better quality responses |
| `gemini-1.5-pro-latest` | Lower | Most capable reasoning |

### Changing the Default Model

Edit `config/settings.py`:

```python
GEMINI_MODEL = "gemini-2.0-flash-lite"   # change this
```

### Feature Flags

```python
# config/settings.py
FEATURE_OBSERVABILITY = True   # show agent trace expanders
FEATURE_EXPORT_PDF    = False  # PDF export (requires weasyprint)
```

---

## Usage Guide

### First-Time Setup (5 minutes)

1. **Launch the app** — `streamlit run app.py`
2. **Add API key** — sidebar → 🔑 API Key → paste → ✅ Save
3. **Select model** — sidebar → 🤖 Model → `gemini-2.0-flash-lite`
4. **Fill onboarding form** — name, current role, dream career, education
5. **Click Launch** — your AI career team is ready

### Recommended Workflow

```
Week 1:  Career Analysis → Skill Assessment → Roadmap Generator
Week 2:  Learning Hub → start logging daily activity
Week 3+: Mock Interviews (2x/week) → Progress Dashboard weekly
Monthly: AI Career Twin → What-If Simulator → adjust strategy
```

### Tips

- **Log activity daily** — the health score depends on your logs. Even 30 minutes counts.
- **Run mock interviews regularly** — the Interview Mentor scores improve your readiness metric.
- **Use What-If before making decisions** — simulate before committing to a new strategy.
- **Check Career Twin monthly** — watch your success probability trend upward.
- **Export your roadmap** — download as Markdown for offline reference.

### Quota Management

The free Gemini tier allows:
- **1,500 requests/day** on `gemini-2.0-flash-lite`
- **15 requests/minute**

Each agent call uses 1 request. A full onboarding pipeline (Career Analysis + Skill Gap + Roadmap + Resources) uses 4 requests.

If you hit a quota limit, wait 60 seconds and retry — or switch to `gemini-2.0-flash` in the sidebar.

---

## API Reference

### BaseAgent

All agents inherit from `BaseAgent`. Key methods:

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    name = "My Agent"
    system_prompt = "You are a helpful expert..."

    def run(self, input: str, user_id: int = None) -> dict:
        prompt = f"Process this: {input}"
        return self._call_and_parse(prompt, user_id=user_id, action="run")
```

| Method | Description |
|---|---|
| `_call(prompt, ...)` | Call Gemini, return raw text |
| `_call_structured(prompt, ...)` | Call Gemini, expect JSON, return raw text |
| `_call_and_parse(prompt, ...)` | Call Gemini + parse JSON, return dict |
| `_parse_json(text)` | Strip markdown fences, parse JSON |
| `save_message(user_id, role, content)` | Save to conversation history |
| `get_history(user_id, limit)` | Load conversation history |

### Orchestrator

```python
from agents.orchestrator import Orchestrator

orch = Orchestrator()

# Full onboarding pipeline (4 agent calls)
results = orch.run_full_analysis(
    user_id=1,
    dream_career="AI Engineer",
    user_profile={"current_role": "Student", "experience_years": 0},
    user_skills=[{"name": "Python", "level": 3}],
    daily_hours=2,
)
# results = {career_analysis, skill_gap, roadmap, resources, goal_id}

# Weekly health check
snapshot = orch.run_weekly_health_check(user_id=1, user_profile=user)
# snapshot = {health_score, weekly_plan, career_twin}

# What-If simulation
result = orch.run_whatif("What if I skip DSA?", user_id=1, user_profile=user)
```

### Database Helpers

```python
from database import db

# Users
uid = db.upsert_user(name, email, current_role, experience_years, education, dream_career)
user = db.get_user(uid)

# Skills
db.save_skills(uid, [{"name": "Python", "category": "Programming", "level": 3}])
skills = db.get_skills(uid)

# Progress
db.log_progress(uid, "Building project", "Built CNN classifier", hours=2.5, milestone=True)
logs = db.get_progress(uid, limit=30)

# Health scores
db.save_health_score(uid, learning=76, skill_dev=65, project=48, interview=80, overall=67.25, feedback="...")
scores = db.get_health_scores(uid, limit=10)

# Agent logs
db.log_agent(uid, "Career Analyst Agent", "analyze_career", input_data, output_data, exec_ms, "success")
logs = db.get_agent_logs(uid, limit=100)
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Fix |
|---|---|---|
| `404 NOT_FOUND` | Wrong model name | Use `gemini-2.0-flash-lite` in sidebar |
| `429 RESOURCE_EXHAUSTED` | Free quota hit | Wait 60s or switch to `gemini-2.0-flash` |
| `SyntaxError: return outside function` | Old page files | Download fresh zip and replace pages/ folder |
| `AttributeError: NoneType has no attribute get` | Empty session state | Complete onboarding on Home page first |
| Emoji filename error on Windows | Old downloaded zip | Download the latest zip and delete old folder |

### Windows-Specific

If you see garbled filenames like `04_≡ƒù║∩╕Å_Roadmap_Generator.py`, run:

```bash
python fix_filenames.py
```

This renames all page files to their clean equivalents.

### Reset Everything

```bash
# Delete the database and start fresh
del dream_career.db          # Windows
rm dream_career.db           # Mac/Linux

# Restart the app
streamlit run app.py
```

---

## Contributing

Contributions welcome. The codebase is intentionally modular so individual components are easy to improve without affecting others.

### Adding a New Agent

1. Create `agents/my_agent.py` inheriting from `BaseAgent`
2. Add your system prompt to `config/prompts.py`
3. Add any constants to `config/constants.py`
4. Register the agent in `agents/orchestrator.py`
5. Create a page in `pages/` following the flat-script pattern

### Adding a New Page

Each page follows this template:

```python
import streamlit as st
st.set_page_config(page_title="Page Title | Dream-to-Career AI", page_icon="🎯", layout="wide")

import os
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles

init_db(); init_session(); apply_styles()

# Sidebar (copy from any existing page)
with st.sidebar:
    # ... standard sidebar block ...

# Guard: require login
if not st.session_state.get("user_id"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

# Page content here
# Use st.stop() instead of return to halt execution
```

---

## License

MIT License — free to use, modify, and distribute.

---

## Acknowledgements

Built with:
- [Google Gemini](https://ai.google.dev/) — AI reasoning engine
- [Streamlit](https://streamlit.io/) — Python web framework
- [Plotly](https://plotly.com/) — Interactive charts
- [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) — Typography

---

*Hackathon project · Multi-Agent Systems track · Built with Google Gemini API*
