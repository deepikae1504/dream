"""
utils/charts.py
Reusable Plotly chart builders. Every function returns a go.Figure.
Import and pass directly to st.plotly_chart().
"""
from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config.constants import COLORS

P  = COLORS["primary"]
S  = COLORS["secondary"]
A  = COLORS["accent"]
W  = COLORS["warning"]
BG = COLORS["bg_card"]
TM = COLORS["text_main"]
MT = COLORS["text_muted"]

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=MT, family="Space Grotesk"),
    margin=dict(t=40, b=30, l=30, r=30),
)


# ── Gauge / score ring ─────────────────────────────────────────────────────────

def score_gauge(score: float, label: str = "Score", height: int = 220) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": label, "font": {"color": TM, "size": 13}},
        number={"font": {"color": S, "size": 38, "family": "Space Grotesk"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": MT}},
            "bar":  {"color": P},
            "bgcolor": BG,
            "borderwidth": 0,
            "steps": [
                {"range": [0,  40], "color": f"rgba(255,101,132,0.12)"},
                {"range": [40, 70], "color": f"rgba(255,184,77, 0.12)"},
                {"range": [70,100], "color": f"rgba(0,212,170,  0.12)"},
            ],
            "threshold": {
                "line":      {"color": A, "width": 2},
                "thickness": 0.75,
                "value":     score,
            },
        },
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(**_LAYOUT, height=height)
    return fig


# ── Radar chart ────────────────────────────────────────────────────────────────

def radar_chart(
    categories: list[str],
    values: list[float],
    title: str = "Skill Profile",
    height: int = 350,
) -> go.Figure:
    cats   = categories + [categories[0]]
    vals   = values     + [values[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats,
        fill="toself",
        fillcolor=f"rgba(108,99,255,0.18)",
        line=dict(color=P, width=2),
        marker=dict(color=P, size=6),
    ))
    fig.update_layout(
        **_LAYOUT,
        title={"text": title, "font": {"color": TM, "size": 13}},
        polar=dict(
            bgcolor=BG,
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont={"color": MT},
                gridcolor="rgba(255,255,255,0.04)",
            ),
            angularaxis=dict(
                tickfont={"color": TM},
                gridcolor="rgba(255,255,255,0.04)",
            ),
        ),
        height=height,
    )
    return fig


# ── Horizontal bar (skill gaps / comparisons) ──────────────────────────────────

def horizontal_bar(
    labels: list[str],
    values: list[float],
    title: str = "",
    color_scale: bool = True,
    height: int | None = None,
) -> go.Figure:
    colors_list = [
        S if v >= 70 else (P if v >= 40 else A) for v in values
    ] if color_scale else P

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors_list),
        text=[f"{v:.0f}" for v in values],
        textposition="outside",
        textfont=dict(color=MT),
    ))
    h = height or max(200, len(labels) * 42)
    fig.update_layout(
        **_LAYOUT,
        title={"text": title, "font": {"color": TM, "size": 13}},
        xaxis=dict(range=[0, 110], tickfont=dict(color=MT),
                   gridcolor="rgba(255,255,255,0.03)"),
        yaxis=dict(tickfont=dict(color=TM)),
        height=h,
    )
    return fig


# ── Line chart (progress over time) ───────────────────────────────────────────

def progress_line(
    dates: list[str],
    values: list[float],
    label: str = "Hours",
    title: str = "Progress Over Time",
    height: int = 280,
) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=dates, y=values, mode="lines+markers",
        line=dict(color=P, width=2.5),
        marker=dict(color=P, size=6),
        fill="tozeroy",
        fillcolor=f"rgba(108,99,255,0.08)",
        name=label,
    ))
    fig.update_layout(
        **_LAYOUT,
        title={"text": title, "font": {"color": TM, "size": 13}},
        xaxis=dict(tickfont=dict(color=MT), gridcolor="rgba(255,255,255,0.03)"),
        yaxis=dict(tickfont=dict(color=MT), gridcolor="rgba(255,255,255,0.03)"),
        height=height,
    )
    return fig


# ── Multi-line (health scores over weeks) ────────────────────────────────────

def health_history_chart(
    health_rows: list[dict],
    height: int = 300,
) -> go.Figure:
    if not health_rows:
        return go.Figure()

    df = pd.DataFrame(health_rows[::-1])  # oldest first
    weeks = df.get("week_date", list(range(len(df)))).tolist()

    traces = [
        ("learning_consistency", "Learning",   P),
        ("skill_development",    "Skills",     S),
        ("project_building",     "Projects",   A),
        ("interview_readiness",  "Interviews", W),
    ]
    fig = go.Figure()
    for col, name, color in traces:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=weeks, y=df[col].tolist(),
                mode="lines+markers", name=name,
                line=dict(color=color, width=2),
                marker=dict(color=color, size=5),
            ))

    fig.update_layout(
        **_LAYOUT,
        title={"text": "Career Health Scores Over Time",
               "font": {"color": TM, "size": 13}},
        xaxis=dict(tickfont=dict(color=MT), gridcolor="rgba(255,255,255,0.03)"),
        yaxis=dict(range=[0, 100], tickfont=dict(color=MT),
                   gridcolor="rgba(255,255,255,0.03)"),
        legend=dict(font=dict(color=MT), bgcolor="rgba(0,0,0,0)"),
        height=height,
    )
    return fig


# ── Milestone timeline (scatter on a line) ────────────────────────────────────

def milestone_timeline(
    milestones: list[dict],
    height: int = 200,
) -> go.Figure:
    if not milestones:
        return go.Figure()

    months = [m.get("month", i + 1) for i, m in enumerate(milestones)]
    labels = [m.get("milestone", "") for m in milestones]

    fig = go.Figure()
    fig.add_shape(
        type="line",
        x0=0, x1=max(months) + 1, y0=0, y1=0,
        line=dict(color=f"{P}60", width=2),
    )
    fig.add_trace(go.Scatter(
        x=months, y=[0] * len(months),
        mode="markers+text",
        marker=dict(size=14, color=P, symbol="circle",
                    line=dict(color=S, width=2)),
        text=labels,
        textposition="top center",
        textfont=dict(color=MT, size=10),
        hoverinfo="text",
    ))
    fig.update_layout(
        **_LAYOUT,
        xaxis=dict(title="Month", tickfont=dict(color=MT),
                   gridcolor="rgba(255,255,255,0.02)"),
        yaxis=dict(visible=False),
        height=height,
        margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig


# ── Pie / donut (skill distribution) ─────────────────────────────────────────

def skill_donut(
    labels: list[str],
    values: list[int],
    title: str = "Skill Coverage",
    height: int = 300,
) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.55,
        marker=dict(colors=[P, S, A, W, "#A78BFA", "#34D399"]),
        textfont=dict(color=TM),
    ))
    fig.update_layout(
        **_LAYOUT,
        title={"text": title, "font": {"color": TM, "size": 13}},
        legend=dict(font=dict(color=MT), bgcolor="rgba(0,0,0,0)"),
        height=height,
    )
    return fig


# ── What-If comparison bar ────────────────────────────────────────────────────

def whatif_comparison(
    scenarios: list[str],
    probabilities: list[float],
    height: int | None = None,
) -> go.Figure:
    colors = [
        S if p >= 70 else (P if p >= 50 else A) for p in probabilities
    ]
    short = [s[:35] + "…" if len(s) > 35 else s for s in scenarios]
    h = height or max(200, len(scenarios) * 55)

    fig = go.Figure(go.Bar(
        x=probabilities, y=short, orientation="h",
        marker=dict(color=colors),
        text=[f"{p}%" for p in probabilities],
        textposition="outside",
        textfont=dict(color=MT),
    ))
    fig.update_layout(
        **_LAYOUT,
        title={"text": "Scenario Success Probability Comparison",
               "font": {"color": TM, "size": 13}},
        xaxis=dict(range=[0, 110], tickfont=dict(color=MT),
                   gridcolor="rgba(255,255,255,0.03)"),
        yaxis=dict(tickfont=dict(color=TM)),
        height=h,
    )
    return fig
