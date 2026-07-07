"""
utils/ui_components.py - Shared UI helpers and CSS
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Brand colors ──────────────────────────────────────────────────────────────
PRIMARY   = "#6C63FF"   # Indigo/violet
SECONDARY = "#00D4AA"   # Teal
ACCENT    = "#FF6584"   # Coral
BG_DARK   = "#0D0F1C"
BG_CARD   = "#161929"
TEXT_MAIN = "#E8E9F3"
TEXT_MUTED= "#8890B5"

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {{
  --primary: {PRIMARY};
  --secondary: {SECONDARY};
  --accent: {ACCENT};
  --bg-dark: {BG_DARK};
  --bg-card: {BG_CARD};
  --text-main: {TEXT_MAIN};
  --text-muted: {TEXT_MUTED};
}}

html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg-dark) !important;
  color: var(--text-main) !important;
  font-family: 'Space Grotesk', sans-serif !important;
}}

[data-testid="stSidebar"] {{
  background: #10132A !important;
  border-right: 1px solid rgba(108,99,255,0.2) !important;
}}

h1, h2, h3, h4 {{
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important;
  color: var(--text-main) !important;
}}

.stButton > button {{
  background: linear-gradient(135deg, var(--primary), #8B84FF) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  padding: 0.5rem 1.5rem !important;
  transition: all 0.2s !important;
}}

.stButton > button:hover {{
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 20px rgba(108,99,255,0.4) !important;
}}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {{
  background: #1E2235 !important;
  border: 1px solid rgba(108,99,255,0.3) !important;
  border-radius: 8px !important;
  color: var(--text-main) !important;
  font-family: 'Space Grotesk', sans-serif !important;
}}

.stSlider > div > div > div > div {{
  background: var(--primary) !important;
}}

div[data-testid="stMetric"] {{
  background: var(--bg-card) !important;
  border: 1px solid rgba(108,99,255,0.2) !important;
  border-radius: 12px !important;
  padding: 1rem !important;
}}

div[data-testid="stMetricValue"] {{
  color: var(--secondary) !important;
  font-size: 2rem !important;
  font-weight: 700 !important;
}}

.metric-card {{
  background: var(--bg-card);
  border: 1px solid rgba(108,99,255,0.25);
  border-radius: 16px;
  padding: 1.5rem;
  margin: 0.5rem 0;
  transition: border-color 0.2s;
}}

.metric-card:hover {{
  border-color: rgba(108,99,255,0.6);
}}

.agent-badge {{
  display: inline-block;
  background: linear-gradient(135deg, rgba(108,99,255,0.2), rgba(0,212,170,0.15));
  border: 1px solid rgba(108,99,255,0.4);
  border-radius: 20px;
  padding: 0.2rem 0.8rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: {PRIMARY};
  margin-bottom: 0.5rem;
}}

.page-hero {{
  background: linear-gradient(135deg, rgba(108,99,255,0.15), rgba(0,212,170,0.08));
  border: 1px solid rgba(108,99,255,0.2);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
}}

.score-ring {{
  text-align: center;
  padding: 1rem;
}}

.timeline-item {{
  border-left: 2px solid var(--primary);
  padding-left: 1rem;
  margin-bottom: 1rem;
}}

.skill-chip {{
  display: inline-block;
  background: rgba(108,99,255,0.15);
  border: 1px solid rgba(108,99,255,0.3);
  border-radius: 20px;
  padding: 0.2rem 0.7rem;
  font-size: 0.8rem;
  margin: 0.2rem;
  color: var(--text-main);
}}

.gap-chip {{
  background: rgba(255,101,132,0.15) !important;
  border-color: rgba(255,101,132,0.3) !important;
  color: {ACCENT} !important;
}}

.status-ok {{color: {SECONDARY};}}
.status-warn {{color: #FFB84D;}}
.status-bad {{color: {ACCENT};}}

.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  color: var(--text-muted) !important;
  border: none !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 500 !important;
}}

.stTabs [aria-selected="true"] {{
  color: var(--primary) !important;
  border-bottom: 2px solid var(--primary) !important;
}}

/* Hide streamlit default elements */
#MainMenu, footer, header {{visibility: hidden;}}
.stDeployButton {{display: none;}}

/* Expander styling */
.streamlit-expanderHeader {{
  background: var(--bg-card) !important;
  border: 1px solid rgba(108,99,255,0.2) !important;
  border-radius: 8px !important;
  color: var(--text-main) !important;
  font-family: 'Space Grotesk', sans-serif !important;
}}
</style>
"""

def apply_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def page_header(title: str, subtitle: str, agent_name: str = ""):
    badge = f'<div class="agent-badge">🤖 {agent_name}</div>' if agent_name else ""
    st.markdown(f"""
    <div class="page-hero">
        {badge}
        <h1 style="margin:0;font-size:2rem;background:linear-gradient(135deg,{PRIMARY},{SECONDARY});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">{title}</h1>
        <p style="color:{TEXT_MUTED};margin:0.5rem 0 0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def metric_card(title: str, value: str, delta: str = "", icon: str = "📊"):
    color = SECONDARY if not delta.startswith("-") else ACCENT
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:1.5rem;margin-bottom:0.3rem">{icon}</div>
        <div style="color:{TEXT_MUTED};font-size:0.8rem;font-weight:500;text-transform:uppercase;
        letter-spacing:0.05em">{title}</div>
        <div style="color:{color};font-size:1.8rem;font-weight:700;margin:0.3rem 0">{value}</div>
        {f'<div style="color:{TEXT_MUTED};font-size:0.85rem">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def score_gauge(score: float, label: str = "Score"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': label, 'font': {'color': TEXT_MAIN, 'family': 'Space Grotesk', 'size': 14}},
        number={'font': {'color': SECONDARY, 'family': 'Space Grotesk', 'size': 36}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': TEXT_MUTED,
                     'tickfont': {'color': TEXT_MUTED}},
            'bar': {'color': PRIMARY},
            'bgcolor': BG_CARD,
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(255,101,132,0.15)'},
                {'range': [40, 70], 'color': 'rgba(255,184,77,0.15)'},
                {'range': [70, 100], 'color': 'rgba(0,212,170,0.15)'},
            ],
            'threshold': {'line': {'color': ACCENT, 'width': 2},
                          'thickness': 0.75, 'value': score}
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=220, margin=dict(t=30, b=10, l=20, r=20),
        font={'color': TEXT_MAIN, 'family': 'Space Grotesk'}
    )
    return fig

def radar_chart(categories: list, values: list, title: str = "Skills Radar"):
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor=f'rgba(108,99,255,0.2)',
        line=dict(color=PRIMARY, width=2),
        marker=dict(color=PRIMARY)
    ))
    fig.update_layout(
        title={'text': title, 'font': {'color': TEXT_MAIN, 'size': 14}},
        polar=dict(
            bgcolor=BG_CARD,
            radialaxis=dict(visible=True, range=[0, 100],
                           tickfont={'color': TEXT_MUTED}, gridcolor='rgba(255,255,255,0.05)'),
            angularaxis=dict(tickfont={'color': TEXT_MAIN}, gridcolor='rgba(255,255,255,0.05)')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(t=50, b=30, l=30, r=30),
        font={'color': TEXT_MAIN, 'family': 'Space Grotesk'}
    )
    return fig

def progress_timeline(milestones: list):
    """Render a visual timeline of milestones."""
    if not milestones:
        return
    st.markdown("#### 🗓️ Career Journey Timeline")
    for i, m in enumerate(milestones):
        month = m.get("month", i + 1)
        milestone = m.get("milestone", "")
        metric = m.get("metric", "")
        color = SECONDARY if i < 2 else (PRIMARY if i < 3 else TEXT_MUTED)
        icon = "✅" if i < 1 else ("🎯" if i < 3 else "🚀")
        st.markdown(f"""
        <div class="timeline-item" style="border-left-color:{color}">
            <div style="color:{TEXT_MUTED};font-size:0.75rem;font-weight:600">Month {month}</div>
            <div style="font-weight:600;margin:0.2rem 0">{icon} {milestone}</div>
            <div style="color:{TEXT_MUTED};font-size:0.85rem">{metric}</div>
        </div>
        """, unsafe_allow_html=True)

def skill_chips(skills: list, gap: bool = False):
    chips_html = ""
    for s in skills:
        name = s.get("skill", s) if isinstance(s, dict) else s
        extra = ' gap-chip' if gap else ''
        chips_html += f'<span class="skill-chip{extra}">{name}</span>'
    st.markdown(chips_html, unsafe_allow_html=True)

def loading_spinner(message: str = "Agent is thinking..."):
    return st.spinner(f"🤖 {message}")

def agent_trace_expander(agent_name: str, action: str, result_preview: str):
    with st.expander(f"🔍 Agent Trace: {agent_name} → {action}", expanded=False):
        st.code(result_preview[:800], language="json")

def health_score_bars(scores: dict):
    items = [
        ("Learning Consistency", scores.get("learning_consistency", 0), "📚"),
        ("Skill Development",    scores.get("skill_development",    0), "🧠"),
        ("Project Building",     scores.get("project_building",     0), "🔨"),
        ("Interview Readiness",  scores.get("interview_readiness",  0), "🎤"),
    ]
    for label, val, icon in items:
        color = SECONDARY if val >= 70 else ("#FFB84D" if val >= 40 else ACCENT)
        st.markdown(f"""
        <div style="margin-bottom:1rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem">
                <span style="font-size:0.9rem">{icon} {label}</span>
                <span style="color:{color};font-weight:700">{val}/100</span>
            </div>
            <div style="background:rgba(255,255,255,0.05);border-radius:100px;height:8px">
                <div style="background:linear-gradient(90deg,{PRIMARY},{color});
                width:{val}%;height:100%;border-radius:100px;transition:width 1s"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
