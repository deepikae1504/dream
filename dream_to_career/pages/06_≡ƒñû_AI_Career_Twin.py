"""
pages/06_🤖_AI_Career_Twin.py
"""
import streamlit as st
import json
import plotly.graph_objects as go
from agents.career_twin import CareerTwinAgent
from agents.recruiter import RecruiterAgent
from database import db
from utils.session import init_session, login_gate
from utils.ui_components import (apply_styles, page_header, metric_card,
                                  PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD)

def render():
    init_session()
    apply_styles()
    page_header("AI Career Twin", "See your predicted future and optimize your path",
                "AI Career Twin")

    if not login_gate("AI Career Twin"):
        return

    uid = st.session_state.user_id
    user = db.get_user(uid)
    skills = db.get_skills(uid)
    progress = db.get_progress(uid)
    interviews = db.get_interviews(uid)
    health_scores = db.get_health_scores(uid, 1)
    health = health_scores[0] if health_scores else {}

    tab1, tab2 = st.tabs(["🤖 AI Career Twin", "👔 Recruiter Perspective"])

    # ── Tab 1: Career Twin ────────────────────────────────────────────────────
    with tab1:
        saved_twin = db.get_latest_twin(uid)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔮 Generate My Career Twin", use_container_width=True):
                agent = CareerTwinAgent()
                with st.spinner("Creating your AI Career Twin simulation..."):
                    try:
                        twin = agent.predict_future(user, skills, progress, health, uid)
                        st.session_state["career_twin"] = twin
                        db.save_career_twin(
                            uid,
                            str({"skills": len(skills), "progress_days": len(progress)}),
                            json.dumps(twin.get("career_milestones_predicted",[])),
                            json.dumps(twin.get("critical_risks",[])),
                            json.dumps(twin.get("opportunities",[])),
                            json.dumps(twin.get("missing_skills_for_success",[])),
                            twin.get("success_probability", 50),
                            json.dumps(twin.get("career_milestones_predicted",[]))
                        )
                        st.success("✅ Career Twin created!")
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col2:
            if saved_twin and st.button("📂 Load Previous Twin", use_container_width=True):
                # Reconstruct twin from DB
                twin_reconstructed = {
                    "success_probability": saved_twin.get("success_probability", 50),
                    "critical_risks": json.loads(saved_twin.get("risks","[]") or "[]"),
                    "opportunities": json.loads(saved_twin.get("opportunities","[]") or "[]"),
                    "missing_skills_for_success": json.loads(saved_twin.get("missing_skills","[]") or "[]"),
                }
                st.session_state["career_twin"] = twin_reconstructed
                st.rerun()

        twin = st.session_state.get("career_twin")
        if not twin:
            # Teaser
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(108,99,255,0.15),rgba(0,212,170,0.1));
            border:1px solid rgba(108,99,255,0.3);border-radius:20px;padding:2rem;text-align:center;margin:2rem 0">
                <div style="font-size:3rem">🤖</div>
                <h3 style="margin:0.5rem 0">Meet Your AI Career Twin</h3>
                <p style="color:{TEXT_MUTED};max-width:400px;margin:0 auto">
                    Your AI Career Twin is a simulation of your future self. It analyzes your 
                    current trajectory, predicts outcomes, identifies risks, and suggests the 
                    actions most likely to get you to your dream career.
                </p>
            </div>
            """, unsafe_allow_html=True)
            return

        if "raw" in twin:
            st.markdown(twin["raw"])
            return

        # Twin header
        prob = twin.get("success_probability", 50)
        prob_color = SECONDARY if prob >= 70 else (PRIMARY if prob >= 50 else ACCENT)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{BG_CARD},{BG_CARD});
        border:2px solid {prob_color}40;border-radius:20px;padding:2rem;margin:1rem 0;
        position:relative;overflow:hidden">
            <div style="position:absolute;top:0;right:0;width:200px;height:200px;
            background:radial-gradient({prob_color}20,transparent);border-radius:50%;
            transform:translate(50%,-50%)"></div>
            <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
                <div style="font-size:3rem">🤖</div>
                <div>
                    <h2 style="margin:0;color:{prob_color}">{twin.get('twin_name','Future You')}</h2>
                    <p style="color:{TEXT_MUTED};margin:0.3rem 0">{twin.get('current_trajectory','')}</p>
                </div>
                <div style="margin-left:auto;text-align:center">
                    <div style="font-size:3rem;font-weight:700;color:{prob_color}">{prob}%</div>
                    <div style="color:{TEXT_MUTED};font-size:0.85rem">Success Probability</div>
                </div>
            </div>
            <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.05)">
                <em style="color:{SECONDARY}">&ldquo;{twin.get('twin_message','')}&rdquo;</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1: metric_card("Timeline", twin.get("predicted_timeline","12 months"), icon="⏱️")
        with col2: metric_card("First Salary", twin.get("predicted_first_salary","₹--"), icon="💰")
        with col3: metric_card("3-Year Salary", twin.get("predicted_3_year_salary","₹--"), icon="📈")
        with col4: metric_card("Advantage", twin.get("competitive_advantage","Building...")[:20]+"...", icon="⚡")

        # Milestones prediction
        predicted_milestones = twin.get("career_milestones_predicted",[])
        if predicted_milestones:
            st.markdown("### 🗓️ Predicted Career Milestones")
            # Timeline visual
            fig = go.Figure()
            months = [m.get("predicted_month",0) for m in predicted_milestones]
            labels = [m.get("milestone","") for m in predicted_milestones]

            fig.add_trace(go.Scatter(
                x=months, y=[1]*len(months),
                mode='markers+text',
                marker=dict(size=15, color=PRIMARY, symbol='circle'),
                text=labels, textposition='top center',
                textfont=dict(color=TEXT_MUTED, size=11),
            ))
            fig.add_shape(type="line", x0=0, x1=max(months+[12]),
                         y0=1, y1=1, line=dict(color=f"{PRIMARY}40", width=2))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=200, margin=dict(t=60, b=20, l=20, r=20),
                xaxis=dict(title="Month", tickcolor=TEXT_MUTED,
                           tickfont=dict(color=TEXT_MUTED), gridcolor='rgba(255,255,255,0.03)'),
                yaxis=dict(visible=False),
                font=dict(color=TEXT_MUTED, family='Space Grotesk')
            )
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ⚠️ Critical Risks")
            risk_colors = {"High": ACCENT, "Medium": "#FFB84D", "Low": TEXT_MUTED}
            for risk in twin.get("critical_risks", []):
                if isinstance(risk, dict):
                    color = risk_colors.get(risk.get("probability","Medium"), TEXT_MUTED)
                    st.markdown(f"""
                    <div style="background:rgba(255,101,132,0.08);border:1px solid rgba(255,101,132,0.2);
                    border-radius:10px;padding:0.8rem;margin:0.3rem 0">
                        <div style="display:flex;justify-content:space-between">
                            <strong>⚠️ {risk.get('risk','')}</strong>
                            <span style="color:{color};font-size:0.8rem">{risk.get('probability','')}</span>
                        </div>
                        <div style="color:{SECONDARY};font-size:0.8rem;margin-top:0.3rem">
                            🛡️ {risk.get('mitigation','')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 🌟 Opportunities")
            for opp in twin.get("opportunities",[]):
                if isinstance(opp, dict):
                    st.markdown(f"""
                    <div style="background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.2);
                    border-radius:10px;padding:0.8rem;margin:0.3rem 0">
                        <div><strong>🎯 {opp.get('opportunity','')}</strong></div>
                        <div style="color:{SECONDARY};font-size:0.8rem;margin-top:0.3rem">
                            → {opp.get('action_needed','')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("### 🎯 Missing Skills for Success")
        missing = twin.get("missing_skills_for_success",[])
        if missing:
            chips = "".join([
                f'<span style="background:rgba(255,101,132,0.1);border:1px solid rgba(255,101,132,0.3);'
                f'border-radius:20px;padding:0.25rem 0.75rem;margin:0.2rem;display:inline-block;'
                f'font-size:0.85rem;color:{ACCENT}">{s}</span>'
                for s in missing])
            st.markdown(chips, unsafe_allow_html=True)

    # ── Tab 2: Recruiter ──────────────────────────────────────────────────────
    with tab2:
        if st.button("👔 Get Recruiter Evaluation", use_container_width=True):
            agent = RecruiterAgent()
            with st.spinner("Recruiter Perspective Agent evaluating your profile..."):
                try:
                    evaluation = agent.evaluate_profile(user, skills, interviews, uid)
                    st.session_state["recruiter_eval"] = evaluation
                    st.success("✅ Recruiter evaluation complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

        eval_data = st.session_state.get("recruiter_eval")
        if not eval_data:
            st.info("Click the button above to see how a real recruiter would view your profile.")
            return

        if "raw" in eval_data:
            st.markdown(eval_data["raw"])
            return

        prob = eval_data.get("hiring_probability", 30)
        prob_color = SECONDARY if prob >= 60 else (PRIMARY if prob >= 40 else ACCENT)

        st.markdown(f"""
        <div style="background:{BG_CARD};border:2px solid {prob_color}40;border-radius:20px;padding:2rem;margin:1rem 0">
            <div style="display:flex;align-items:center;gap:2rem;flex-wrap:wrap">
                <div style="font-size:2.5rem">👔</div>
                <div style="flex:1">
                    <h3 style="margin:0">Recruiter's First Impression</h3>
                    <p style="color:{TEXT_MUTED};margin:0.3rem 0">{eval_data.get('first_impression','')}</p>
                </div>
                <div style="text-align:center">
                    <div style="font-size:2.5rem;font-weight:700;color:{prob_color}">{prob}%</div>
                    <div style="color:{TEXT_MUTED};font-size:0.85rem">Hire Probability</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:2.5rem;font-weight:700;color:{PRIMARY}">{eval_data.get('profile_grade','C')}</div>
                    <div style="color:{TEXT_MUTED};font-size:0.85rem">Profile Grade</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            metric_card("Expected Offer", eval_data.get("expected_salary_offer","₹--"), icon="💰")
            metric_card("Time to Hireable", eval_data.get("time_to_hireable","Unknown"), icon="⏱️")
            metric_card("Interview Ready", eval_data.get("interview_readiness","No"), icon="🎤")

        with col2:
            st.markdown("### 🎯 Top Action Right Now")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(108,99,255,0.2),rgba(0,212,170,0.1));
            border:1px solid rgba(108,99,255,0.3);border-radius:12px;padding:1rem">
                🚀 {eval_data.get('top_action','')}
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Recruiter Sees These Strengths")
            for s in eval_data.get("strengths_as_recruiter_sees",[]):
                st.markdown(f"✅ {s}")

        with col2:
            st.markdown("### 🚩 Red Flags to Fix")
            for r in eval_data.get("red_flags",[]):
                st.markdown(f"🚩 {r}")

        st.markdown("### 📋 What You Need to Get Shortlisted")
        for item in eval_data.get("missing_for_shortlisting",[]):
            st.markdown(f"• {item}")

        st.markdown("### 📄 Resume Tips")
        for tip in eval_data.get("resume_advice",[]):
            st.markdown(f"💡 {tip}")

        st.markdown(f"""
        <div style="background:rgba(108,99,255,0.08);border-left:4px solid {PRIMARY};
        border-radius:0 12px 12px 0;padding:1rem 1.5rem;margin-top:1rem">
            <strong>Recruiter's Verdict:</strong><br>
            {eval_data.get('recruiter_verdict','')}
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    from utils.sidebar import render_sidebar
    render_sidebar()
    render()
