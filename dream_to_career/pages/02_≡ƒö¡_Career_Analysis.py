"""
pages/02_🔭_Career_Analysis.py
"""
import streamlit as st
import json
from agents.career_analyst import CareerAnalystAgent
from database import db
from utils.session import init_session, login_gate
from utils.ui_components import (apply_styles, page_header, metric_card,
                                  skill_chips, agent_trace_expander,
                                  PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD)

def render():
    init_session()
    apply_styles()
    page_header("Career Analysis", "Deep market intelligence for your target role",
                "Career Analyst Agent")

    if not login_gate("Career Analysis"):
        return

    uid = st.session_state.user_id
    user = db.get_user(uid)

    # ── Input ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
    border-radius:16px;padding:1.5rem;margin-bottom:1.5rem">
    """, unsafe_allow_html=True)

    career_input = st.text_input(
        "Target Career Role",
        value=user.get("dream_career", ""),
        placeholder="e.g. Machine Learning Engineer, Full Stack Developer, Data Scientist"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔭 Analyze This Career", use_container_width=True):
            if career_input:
                agent = CareerAnalystAgent()
                with st.spinner("Career Analyst Agent is researching the market..."):
                    try:
                        result = agent.analyze(career_input, user, uid)
                        st.session_state["career_analysis"] = result
                        # Save to DB
                        goal_id = db.save_career_goal(
                            uid, career_input,
                            career_report=json.dumps(result),
                            required_skills=json.dumps(result.get("required_skills", [])),
                            market_demand=result.get("market_demand", "")
                        )
                        st.session_state["active_goal_id"] = goal_id
                        db.upsert_user(user["name"], user.get("email",""),
                                       user["current_role"], user["experience_years"],
                                       user["education"], career_input)
                        st.success("✅ Career analysis complete!")
                    except Exception as e:
                        st.error(f"Error: {e}")
    with col2:
        # Load from DB
        goal = db.get_active_goal(uid)
        if goal and goal.get("career_report"):
            if st.button("📂 Load Previous Analysis", use_container_width=True):
                st.session_state["career_analysis"] = json.loads(goal["career_report"])
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Results ───────────────────────────────────────────────────────────────
    analysis = st.session_state.get("career_analysis")
    if not analysis:
        st.info("Enter a career above and click **Analyze** to see detailed insights.")
        return

    if "raw" in analysis:
        st.markdown(analysis["raw"])
        return

    # Header metrics
    st.markdown(f"## {analysis.get('career_title', career_input)}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Market Demand", analysis.get("market_demand","N/A").split()[0],
                    icon="📈")
    with col2:
        metric_card("Avg. Salary", analysis.get("avg_salary_range","₹--"), icon="💰")
    with col3:
        req_skills = analysis.get("required_skills", [])
        metric_card("Skills Required", str(len(req_skills)), icon="🧠")
    with col4:
        metric_card("Top Companies", str(len(analysis.get("top_companies",[]))), icon="🏢")

    # Overview
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(108,99,255,0.08);border-left:4px solid {PRIMARY};
    border-radius:0 12px 12px 0;padding:1rem 1.5rem;margin-bottom:1.5rem">
        <p style="margin:0;font-size:1.05rem">{analysis.get('overview','')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Required skills
    st.markdown("### 🧠 Required Skills")
    tab1, tab2, tab3 = st.tabs(["All Skills", "Technical", "Soft Skills"])

    all_skills = analysis.get("required_skills", [])
    with tab1:
        skill_chips(all_skills)
    with tab2:
        tech = [s for s in all_skills if s.get("category","") == "Technical"]
        skill_chips(tech if tech else all_skills)
    with tab3:
        soft = [s for s in all_skills if s.get("category","") in ("Soft","Domain")]
        skill_chips(soft if soft else [])

    # Career stages
    st.markdown("### 🪜 Career Progression")
    stages = analysis.get("career_stages", [])
    if stages:
        cols = st.columns(len(stages))
        for i, (col, stage) in enumerate(zip(cols, stages)):
            with col:
                color = [PRIMARY, SECONDARY, ACCENT, "#FFB84D"][i % 4]
                st.markdown(f"""
                <div style="background:{BG_CARD};border:1px solid {color}40;
                border-radius:12px;padding:1rem;text-align:center;border-top:3px solid {color}">
                    <div style="font-weight:700;color:{color}">{stage.get('stage','')}</div>
                    <div style="color:{TEXT_MUTED};font-size:0.8rem;margin:0.3rem 0">
                        {stage.get('timeline','')}
                    </div>
                    <div style="font-size:0.85rem">{stage.get('salary','')}</div>
                </div>
                """, unsafe_allow_html=True)

    # Top companies
    st.markdown("### 🏢 Top Companies Hiring")
    companies = analysis.get("top_companies", [])
    if companies:
        chips = "".join([
            f'<span style="background:rgba(0,212,170,0.1);border:1px solid rgba(0,212,170,0.3);'
            f'border-radius:20px;padding:0.3rem 0.8rem;margin:0.2rem;display:inline-block;'
            f'font-size:0.85rem">{c}</span>'
            for c in companies])
        st.markdown(chips, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌱 Growth Outlook")
        st.markdown(f"""
        <div style="background:{BG_CARD};border-radius:12px;padding:1rem">
            {analysis.get('growth_outlook','')}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎖️ Key Certifications")
        for cert in analysis.get("key_certifications",[]):
            st.markdown(f"• {cert}")

    with col2:
        st.markdown("### ✅ Success Factors")
        for f in analysis.get("success_factors",[]):
            st.markdown(f"✅ {f}")

        st.markdown("### ⚠️ Challenges")
        for c in analysis.get("challenges",[]):
            st.markdown(f"⚠️ {c}")

    # Daily life
    st.markdown("### 🗓️ A Typical Day")
    st.info(analysis.get("daily_work",""))

    agent_trace_expander("Career Analyst Agent", "analyze", json.dumps(analysis, indent=2)[:600])

    # CTA
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("▶️ Next: Assess My Skills", use_container_width=True):
        st.switch_page("pages/03_🧩_Skill_Assessment.py")


if __name__ == "__main__":
    from utils.sidebar import render_sidebar
    render_sidebar()
    render()
