import streamlit as st
st.set_page_config(page_title="What-If Simulator | Dream-to-Career AI", page_icon="⚡", layout="wide")
import os
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from agents.whatif_agent import WhatIfAgent
from config.constants import WHATIF_PRESETS

init_db(); init_session(); apply_styles()

with st.sidebar:
    st.markdown("### 🔑 API Key")
    if not st.session_state.get("api_key"):
        _e = os.environ.get("GEMINI_API_KEY","")
        if _e: st.session_state.api_key = _e
    _t = st.text_input("Key", value=st.session_state.get("api_key",""), type="password",
        placeholder="Paste API key...", label_visibility="collapsed", key="sb_key")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("✅ Save", key="sb_save", use_container_width=True):
            if _t and len(_t.strip())>5: st.session_state.api_key=_t.strip(); st.rerun()
            else: st.error("Paste key first")
    with c2:
        if st.button("🗑️ Clear", key="sb_clr", use_container_width=True):
            st.session_state.api_key=""; st.rerun()
    if st.session_state.get("api_key"): st.success("✅ Key Active")
    else: st.warning("⚠️ No key set")
    st.markdown("---")
    _models = ["gemini-2.0-flash-lite","gemini-2.0-flash","gemini-1.5-pro-latest"]
    _cur = st.session_state.get("gemini_model","gemini-2.0-flash-lite")
    if _cur not in _models: _cur = "gemini-2.0-flash-lite"
    _ch = st.selectbox("Model", _models, index=_models.index(_cur), label_visibility="collapsed", key="sb_model")
    if _ch != _cur: st.session_state.gemini_model=_ch; st.rerun()
    st.markdown("---")
    for _p,_l in [("pages/01_Home.py","🏠 Home"),("pages/02_Career_Analysis.py","🔭 Career Analysis"),
        ("pages/03_Skill_Assessment.py","🧩 Skill Assessment"),("pages/04_Roadmap_Generator.py","🗺️ Roadmap"),
        ("pages/05_Learning_Hub.py","📚 Learning Hub"),("pages/06_AI_Career_Twin.py","🤖 Career Twin"),
        ("pages/07_WhatIf_Simulator.py","⚡ What-If"),("pages/08_Mock_Interview.py","🎤 Interview"),
        ("pages/09_Progress_Dashboard.py","📈 Dashboard"),("pages/10_Analytics.py","🔬 Analytics")]:
        if st.button(_l, key=f"nav_{_l}", use_container_width=True): st.switch_page(_p)

if not st.session_state.get("user_id"):
    st.warning("Please complete onboarding on the Home page first."); st.stop()

uid         = st.session_state.user_id
user        = db.get_user(uid) or {}
health_rows = db.get_health_scores(uid,1) or []
health      = health_rows[0] if health_rows else {}

page_header("What-If Simulator","Simulate different choices and see their impact","What-If Simulator")

st.markdown("### ⚡ Quick Scenarios — click any to try it")
cols = st.columns(2)
for i, scenario in enumerate(WHATIF_PRESETS[:8]):
    with cols[i%2]:
        if st.button(f"💭 {scenario[:60]}", key=f"pre_{i}", use_container_width=True):
            st.session_state["whatif_input"] = scenario
            st.rerun()

scenario_text = st.text_area(
    "Or write your own scenario",
    value=st.session_state.get("whatif_input",""),
    height=80,
    placeholder="What if I study 4 hours daily? / What if I skip DSA?...")

col1,col2 = st.columns([3,1])
with col1: simulate = st.button("⚡ Simulate This Scenario", use_container_width=True)
with col2:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.pop("whatif_results", None)
        st.session_state.pop("whatif_input", None)
        st.rerun()

if simulate and scenario_text:
    with st.spinner("Simulating your scenario..."):
        try:
            result = WhatIfAgent().simulate(scenario_text, user, health, uid)
            db.save_whatif(uid, scenario_text, {},
                result.get("long_term_impact",""),
                result.get("timeline_change",""),
                result.get("new_success_probability",50),
                result.get("verdict_reason",""))
            if "whatif_results" not in st.session_state:
                st.session_state["whatif_results"] = []
            st.session_state["whatif_results"].insert(0, {"scenario":scenario_text,"result":result})
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")
elif simulate:
    st.warning("Please enter or select a scenario first.")

results = st.session_state.get("whatif_results",[])
if not results:
    st.info("Select a quick scenario above or write your own, then click **⚡ Simulate**.")
    st.stop()

st.markdown("---")
st.markdown("## 📊 Simulation Results")

for entry in results:
    scenario = entry.get("scenario","")
    result   = entry.get("result",{})
    if not result or "raw" in result: continue

    verdict = result.get("verdict","Neutral")
    color   = SECONDARY if verdict=="Recommended" else (ACCENT if verdict=="Not Recommended" else PRIMARY)
    icon    = "✅" if verdict=="Recommended" else ("❌" if verdict=="Not Recommended" else "⚠️")
    prob    = result.get("new_success_probability",50)
    change  = result.get("success_probability_change","")
    timeline= result.get("timeline_change","No change")

    st.markdown(f"""<div style="background:{BG_CARD};border:2px solid {color}40;
    border-radius:16px;padding:1.5rem;margin:1rem 0">
    <h3 style="margin:0 0 1rem">💭 {scenario}</h3>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem">
        <div style="text-align:center;background:rgba(108,99,255,0.08);border-radius:10px;padding:0.8rem">
            <div style="font-size:2rem;font-weight:700;color:{color}">{prob}%</div>
            <div style="color:{TEXT_MUTED};font-size:0.75rem">New Success Probability</div>
        </div>
        <div style="text-align:center;background:rgba(108,99,255,0.08);border-radius:10px;padding:0.8rem">
            <div style="font-size:1.3rem;font-weight:700;color:{SECONDARY}">{change}</div>
            <div style="color:{TEXT_MUTED};font-size:0.75rem">Probability Change</div>
        </div>
        <div style="text-align:center;background:rgba(108,99,255,0.08);border-radius:10px;padding:0.8rem">
            <div style="font-size:1.1rem;font-weight:700;color:{ACCENT}">{timeline}</div>
            <div style="color:{TEXT_MUTED};font-size:0.75rem">Timeline Impact</div>
        </div>
    </div></div>""", unsafe_allow_html=True)

    with st.expander(f"{icon} {verdict} — See full analysis"):
        col1,col2 = st.columns(2)
        with col1:
            st.markdown(f"**🌱 Short-term (30 days)**  \n{result.get('short_term_impact','')}")
            st.markdown(f"**🔥 Medium-term (3-6 months)**  \n{result.get('medium_term_impact','')}")
            st.markdown(f"**🚀 Long-term (1-2 years)**  \n{result.get('long_term_impact','')}")
        with col2:
            st.markdown("**Pros:**")
            for p in result.get("pros",[]): st.markdown(f"✅ {p}")
            st.markdown("**Cons:**")
            for c in result.get("cons",[]): st.markdown(f"❌ {c}")
        st.info(result.get("verdict_reason",""))
        alt = result.get("alternative_suggestion","")
        if alt: st.success(f"💡 Better alternative: {alt}")
    st.markdown("---")
