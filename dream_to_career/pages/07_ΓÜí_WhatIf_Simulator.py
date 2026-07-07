"""
pages/07_⚡_WhatIf_Simulator.py
"""
import streamlit as st
import plotly.graph_objects as go
from agents.whatif_agent import WhatIfAgent
from database import db
from utils.session import init_session, login_gate
from config.constants import WHATIF_PRESETS
from utils.ui_components import (apply_styles, page_header,
                                  PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD)

PRESET_SCENARIOS = WHATIF_PRESETS

def render():
    init_session()
    apply_styles()
    page_header("What-If Simulator", "Simulate different choices and see their impact",
                "What-If Simulator")

    if not login_gate("What-If Simulator"):
        return

    uid = st.session_state.user_id
    user = db.get_user(uid)
    health_scores = db.get_health_scores(uid, 1)
    health = health_scores[0] if health_scores else {}

    st.markdown(f"""
    <div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
    border-radius:16px;padding:1.5rem;margin-bottom:1.5rem">
        <p style="color:{TEXT_MUTED};margin:0">
            Curious what happens if you change your study strategy? 
            Simulate any scenario and get an AI-powered prediction of the outcome.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Preset scenarios
    st.markdown("### ⚡ Quick Scenarios")
    cols = st.columns(2)
    for i, scenario in enumerate(PRESET_SCENARIOS[:6]):
        with cols[i % 2]:
            if st.button(f"💭 {scenario[:50]}...", key=f"preset_{i}", use_container_width=True):
                st.session_state["whatif_input"] = scenario

    # Custom scenario
    st.markdown("### 🔮 Custom Scenario")
    scenario_text = st.text_area(
        "Describe your scenario",
        value=st.session_state.get("whatif_input",""),
        placeholder="What if I... (describe a learning choice or strategy change)",
        height=100
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        simulate_btn = st.button("⚡ Simulate This Scenario", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ Clear History", use_container_width=True)

    if clear_btn:
        st.session_state.pop("whatif_results", None)
        st.rerun()

    if simulate_btn and scenario_text:
        agent = WhatIfAgent()
        with st.spinner("What-If Simulator running your scenario..."):
            try:
                result = agent.simulate(scenario_text, user, health, uid)
                db.save_whatif(
                    uid, scenario_text, {},
                    result.get("long_term_impact",""),
                    result.get("timeline_change",""),
                    result.get("new_success_probability", 50),
                    result.get("verdict_reason","")
                )
                if "whatif_results" not in st.session_state:
                    st.session_state["whatif_results"] = []
                st.session_state["whatif_results"].insert(0, {"scenario": scenario_text, "result": result})
                st.success("✅ Simulation complete!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Show results
    results = st.session_state.get("whatif_results", [])
    if not results:
        # Show history from DB
        db_history = db.get_whatif_history(uid)
        if not db_history:
            st.info("Try one of the preset scenarios above or write your own.")
        return

    st.markdown("---")
    st.markdown("## 📊 Simulation Results")

    for entry in results:
        scenario = entry.get("scenario","")
        result = entry.get("result", {})

        if not result or "raw" in result:
            if result and "raw" in result:
                st.markdown(result["raw"])
            continue

        verdict = result.get("verdict","Neutral")
        verdict_colors = {"Recommended": SECONDARY, "Not Recommended": ACCENT, "Neutral": PRIMARY}
        verdict_icons = {"Recommended": "✅", "Not Recommended": "❌", "Neutral": "⚠️"}
        v_color = verdict_colors.get(verdict, PRIMARY)
        v_icon = verdict_icons.get(verdict, "⚠️")

        prob = result.get("new_success_probability", 50)
        prob_change = result.get("success_probability_change","")

        st.markdown(f"""
        <div style="background:{BG_CARD};border:2px solid {v_color}40;border-radius:20px;
        padding:1.5rem;margin:1rem 0">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem">
                <div style="flex:1">
                    <div style="color:{TEXT_MUTED};font-size:0.8rem;margin-bottom:0.3rem">SCENARIO</div>
                    <h3 style="margin:0;font-size:1.1rem">💭 {scenario}</h3>
                </div>
                <div style="text-align:center;padding:0.5rem 1rem;
                background:{v_color}20;border-radius:10px;border:1px solid {v_color}40">
                    <div style="font-size:1.5rem">{v_icon}</div>
                    <div style="color:{v_color};font-weight:700;font-size:0.9rem">{verdict}</div>
                </div>
            </div>
            
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1rem">
                <div style="text-align:center;padding:0.8rem;background:rgba(108,99,255,0.08);border-radius:10px">
                    <div style="font-size:1.5rem;font-weight:700;color:{PRIMARY}">{prob}%</div>
                    <div style="color:{TEXT_MUTED};font-size:0.75rem">New Success Probability</div>
                </div>
                <div style="text-align:center;padding:0.8rem;background:rgba(108,99,255,0.08);border-radius:10px">
                    <div style="font-size:1.2rem;font-weight:700;color:{SECONDARY}">{prob_change}</div>
                    <div style="color:{TEXT_MUTED};font-size:0.75rem">Probability Change</div>
                </div>
                <div style="text-align:center;padding:0.8rem;background:rgba(108,99,255,0.08);border-radius:10px">
                    <div style="font-size:1.2rem;font-weight:700;color:{ACCENT}">{result.get('timeline_change','No change')}</div>
                    <div style="color:{TEXT_MUTED};font-size:0.75rem">Timeline Impact</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📋 Full Analysis", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**🌱 Short-term (30 days):**  \n{result.get('short_term_impact','')}")
                st.markdown(f"**🔥 Medium-term (3-6 months):**  \n{result.get('medium_term_impact','')}")
                st.markdown(f"**🚀 Long-term (1-2 years):**  \n{result.get('long_term_impact','')}")

            with col2:
                st.markdown("**✅ Pros:**")
                for pro in result.get("pros",[]):
                    st.markdown(f"✅ {pro}")
                st.markdown("**❌ Cons:**")
                for con in result.get("cons",[]):
                    st.markdown(f"❌ {con}")

            st.markdown(f"""
            <div style="background:rgba(108,99,255,0.08);border-left:4px solid {PRIMARY};
            padding:1rem;border-radius:0 8px 8px 0;margin-top:0.5rem">
                <strong>Verdict:</strong> {result.get('verdict_reason','')}
            </div>
            """, unsafe_allow_html=True)

            if result.get("alternative_suggestion"):
                st.markdown(f"""
                <div style="background:rgba(0,212,170,0.08);border-left:4px solid {SECONDARY};
                padding:1rem;border-radius:0 8px 8px 0;margin-top:0.5rem">
                    <strong>💡 Better Alternative:</strong> {result.get('alternative_suggestion','')}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

    # Comparison chart if multiple results
    if len(results) >= 2:
        st.markdown("### 📊 Scenario Comparison")
        scenarios_short = [r["scenario"][:30]+"..." for r in results[:5]]
        probs = [r["result"].get("new_success_probability",50) for r in results[:5]]

        fig = go.Figure(go.Bar(
            x=probs, y=scenarios_short, orientation='h',
            marker=dict(
                color=probs,
                colorscale=[[0, ACCENT], [0.5, PRIMARY], [1, SECONDARY]],
                showscale=False
            ),
            text=[f"{p}%" for p in probs], textposition='outside',
            textfont=dict(color=TEXT_MUTED)
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(range=[0,100], tickfont=dict(color=TEXT_MUTED),
                       gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(tickfont=dict(color=TEXT_MUTED)),
            height=max(200, len(results[:5]) * 60),
            margin=dict(t=20, b=20, l=200, r=60),
            font=dict(color=TEXT_MUTED, family='Space Grotesk')
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    from utils.sidebar import render_sidebar
    render_sidebar()
    render()
