"""
database/db.py - SQLite database setup and operations
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = "dream_career.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        current_role TEXT,
        experience_years INTEGER DEFAULT 0,
        education TEXT,
        dream_career TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        skill_name TEXT NOT NULL,
        category TEXT,
        proficiency_level INTEGER DEFAULT 1,
        verified INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS career_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        target_career TEXT NOT NULL,
        target_timeline_months INTEGER DEFAULT 12,
        motivation TEXT,
        career_report TEXT,
        required_skills TEXT,
        market_demand TEXT,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        goal_id INTEGER,
        plan_30_day TEXT,
        plan_90_day TEXT,
        plan_6_month TEXT,
        plan_1_year TEXT,
        milestones TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (goal_id) REFERENCES career_goals(id)
    );

    CREATE TABLE IF NOT EXISTS learning_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        skill_name TEXT,
        resource_type TEXT,
        title TEXT,
        url TEXT,
        platform TEXT,
        is_free INTEGER DEFAULT 1,
        priority INTEGER DEFAULT 1,
        status TEXT DEFAULT 'recommended',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS progress_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT DEFAULT CURRENT_DATE,
        activity_type TEXT,
        description TEXT,
        hours_spent REAL DEFAULT 0,
        milestone_completed INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        interview_type TEXT,
        questions TEXT,
        answers TEXT,
        scores TEXT,
        overall_score REAL,
        feedback TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS career_twin_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        current_state TEXT,
        predicted_outcomes TEXT,
        risks TEXT,
        opportunities TEXT,
        missing_skills TEXT,
        success_probability REAL,
        action_suggestions TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS whatif_simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        scenario TEXT,
        parameters TEXT,
        predicted_outcome TEXT,
        timeline_impact TEXT,
        success_probability REAL,
        recommendation TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS career_health_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        week_date TEXT,
        learning_consistency INTEGER DEFAULT 0,
        skill_development INTEGER DEFAULT 0,
        project_building INTEGER DEFAULT 0,
        interview_readiness INTEGER DEFAULT 0,
        overall_score REAL DEFAULT 0,
        feedback TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        agent_name TEXT,
        action TEXT,
        input_data TEXT,
        output_data TEXT,
        execution_time_ms INTEGER,
        status TEXT DEFAULT 'success',
        error_message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        agent_name TEXT,
        role TEXT,
        content TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

# ── User helpers ──────────────────────────────────────────────────────────────

def upsert_user(name, email="", current_role="", experience_years=0,
                education="", dream_career=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (name, email, current_role, experience_years, education, dream_career)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            name=excluded.name, current_role=excluded.current_role,
            experience_years=excluded.experience_years, education=excluded.education,
            dream_career=excluded.dream_career, updated_at=CURRENT_TIMESTAMP
    """, (name, email or f"{name.lower().replace(' ','_')}@user.local",
          current_role, experience_years, education, dream_career))
    conn.commit()
    user_id = cur.lastrowid or cur.execute(
        "SELECT id FROM users WHERE email=?",
        (email or f"{name.lower().replace(' ','_')}@user.local",)).fetchone()[0]
    conn.close()
    return user_id

def get_user(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── Skills ────────────────────────────────────────────────────────────────────

def save_skills(user_id, skills_list):
    conn = get_connection()
    conn.execute("DELETE FROM skills WHERE user_id=?", (user_id,))
    for s in skills_list:
        conn.execute("""INSERT INTO skills (user_id, skill_name, category, proficiency_level)
                        VALUES (?, ?, ?, ?)""",
                     (user_id, s.get("name",""), s.get("category","General"),
                      s.get("level", 1)))
    conn.commit()
    conn.close()

def get_skills(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM skills WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Career goals ──────────────────────────────────────────────────────────────

def save_career_goal(user_id, target_career, timeline_months=12,
                     motivation="", career_report="", required_skills="",
                     market_demand=""):
    conn = get_connection()
    conn.execute("UPDATE career_goals SET status='archived' WHERE user_id=?", (user_id,))
    cur = conn.execute("""
        INSERT INTO career_goals (user_id, target_career, target_timeline_months,
            motivation, career_report, required_skills, market_demand)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, target_career, timeline_months, motivation,
          career_report, required_skills, market_demand))
    conn.commit()
    goal_id = cur.lastrowid
    conn.close()
    return goal_id

def get_active_goal(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM career_goals WHERE user_id=? AND status='active' ORDER BY id DESC LIMIT 1",
        (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── Roadmap ───────────────────────────────────────────────────────────────────

def save_roadmap(user_id, goal_id, plan_30, plan_90, plan_6m, plan_1y, milestones):
    conn = get_connection()
    conn.execute("""
        INSERT INTO roadmaps (user_id, goal_id, plan_30_day, plan_90_day,
            plan_6_month, plan_1_year, milestones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, goal_id, plan_30, plan_90, plan_6m, plan_1y,
          json.dumps(milestones) if isinstance(milestones, list) else milestones))
    conn.commit()
    conn.close()

def get_latest_roadmap(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM roadmaps WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── Progress ──────────────────────────────────────────────────────────────────

def log_progress(user_id, activity_type, description, hours=0,
                 milestone_completed=False, notes=""):
    conn = get_connection()
    conn.execute("""INSERT INTO progress_tracking
        (user_id, activity_type, description, hours_spent, milestone_completed, notes)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, activity_type, description, hours,
         1 if milestone_completed else 0, notes))
    conn.commit()
    conn.close()

def get_progress(user_id, limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM progress_tracking WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Interviews ────────────────────────────────────────────────────────────────

def save_interview(user_id, interview_type, questions, answers,
                   scores, overall_score, feedback):
    conn = get_connection()
    cur = conn.execute("""INSERT INTO interviews
        (user_id, interview_type, questions, answers, scores, overall_score, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, interview_type,
         json.dumps(questions) if isinstance(questions, list) else questions,
         json.dumps(answers)   if isinstance(answers,   list) else answers,
         json.dumps(scores)    if isinstance(scores,    dict) else scores,
         overall_score, feedback))
    conn.commit()
    iid = cur.lastrowid
    conn.close()
    return iid

def get_interviews(user_id, limit=10):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM interviews WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Career twin ───────────────────────────────────────────────────────────────

def save_career_twin(user_id, current_state, predicted_outcomes, risks,
                     opportunities, missing_skills, success_prob, actions):
    conn = get_connection()
    cur = conn.execute("""INSERT INTO career_twin_predictions
        (user_id, current_state, predicted_outcomes, risks, opportunities,
         missing_skills, success_probability, action_suggestions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, current_state, predicted_outcomes, risks, opportunities,
         missing_skills, success_prob, actions))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid

def get_latest_twin(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM career_twin_predictions WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── What-If ───────────────────────────────────────────────────────────────────

def save_whatif(user_id, scenario, parameters, outcome, timeline_impact,
                success_prob, recommendation):
    conn = get_connection()
    cur = conn.execute("""INSERT INTO whatif_simulations
        (user_id, scenario, parameters, predicted_outcome, timeline_impact,
         success_probability, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, scenario,
         json.dumps(parameters) if isinstance(parameters, dict) else parameters,
         outcome, timeline_impact, success_prob, recommendation))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid

def get_whatif_history(user_id, limit=10):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM whatif_simulations WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Health scores ─────────────────────────────────────────────────────────────

def save_health_score(user_id, learning, skill_dev, project, interview_r, overall, feedback):
    conn = get_connection()
    week = datetime.now().strftime("%Y-W%W")
    conn.execute("""
        INSERT INTO career_health_scores
        (user_id, week_date, learning_consistency, skill_development,
         project_building, interview_readiness, overall_score, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, week, learning, skill_dev, project, interview_r, overall, feedback))
    conn.commit()
    conn.close()

def get_health_scores(user_id, limit=10):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM career_health_scores WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Agent logs ────────────────────────────────────────────────────────────────

def log_agent(user_id, agent_name, action, input_data="",
              output_data="", exec_ms=0, status="success", error=""):
    conn = get_connection()
    conn.execute("""INSERT INTO agent_logs
        (user_id, agent_name, action, input_data, output_data,
         execution_time_ms, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, agent_name, action, str(input_data)[:2000],
         str(output_data)[:2000], exec_ms, status, error))
    conn.commit()
    conn.close()

def get_agent_logs(user_id=None, limit=100):
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            "SELECT * FROM agent_logs WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM agent_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Conversation history ──────────────────────────────────────────────────────

def save_message(user_id, agent_name, role, content):
    conn = get_connection()
    conn.execute("""INSERT INTO conversation_history (user_id, agent_name, role, content)
                    VALUES (?, ?, ?, ?)""",
                 (user_id, agent_name, role, content))
    conn.commit()
    conn.close()

def get_conversation(user_id, agent_name, limit=20):
    conn = get_connection()
    rows = conn.execute("""SELECT role, content FROM conversation_history
        WHERE user_id=? AND agent_name=? ORDER BY id DESC LIMIT ?""",
        (user_id, agent_name, limit)).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

# ── Learning resources ────────────────────────────────────────────────────────

def save_resources(user_id, resources_list):
    conn = get_connection()
    for r in resources_list:
        conn.execute("""INSERT INTO learning_resources
            (user_id, skill_name, resource_type, title, url, platform, is_free, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, r.get("skill",""), r.get("type","course"),
             r.get("title",""), r.get("url",""), r.get("platform",""),
             1 if r.get("free", True) else 0, r.get("priority", 1)))
    conn.commit()
    conn.close()

def get_resources(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM learning_resources WHERE user_id=? ORDER BY priority",
        (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
