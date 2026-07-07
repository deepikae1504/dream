import streamlit as st
st.set_page_config(page_title="Mock Interview | Dream-to-Career AI", page_icon="🎤", layout="wide")
import os, json
from database.db import init_db
from database import db
from utils.session import init_session
from utils.ui_components import apply_styles, page_header, score_gauge, PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD
from agents.interview_mentor import InterviewMentorAgent
from config.constants import INTERVIEW_TYPES, INTERVIEW_DIFFICULTY
from utils.validators import validate_interview_answer

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

uid    = st.session_state.user_id
user   = db.get_user(uid) or {}
career = user.get("dream_career","Software Engineer")
agent  = InterviewMentorAgent()

page_header("Mock Interview","Practice with AI and get detailed feedback","Interview Mentor Agent")

# ── SETUP SCREEN ───────────────────────────────────────────────────────────────
if not st.session_state.get("interview_active"):
    col1,col2,col3 = st.columns(3)
    with col1: itype = st.selectbox("Interview Type", INTERVIEW_TYPES)
    with col2: diff  = st.selectbox("Difficulty", INTERVIEW_DIFFICULTY)
    with col3: nq    = st.selectbox("Number of Questions", [3,5,7,10], index=1)

    col1,col2 = st.columns(2)
    with col1:
        if st.button("🎤 Start Mock Interview", use_container_width=True):
            with st.spinner("Generating questions..."):
                try:
                    qs = agent.generate_questions(career, itype, diff, nq, uid)
                    if not qs: st.error("No questions generated. Try again."); st.stop()
                    st.session_state.update({
                        "interview_questions": qs,
                        "interview_answers": {},
                        "interview_evaluations": {},
                        "interview_active": True,
                        "interview_complete": False,
                        "interview_final_feedback": None,
                        "interview_type": itype,
                        "current_q": 0,
                    })
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
    with col2:
        past = db.get_interviews(uid) or []
        if past:
            st.markdown(f"**Past interviews: {len(past)}**")
            for iv in past[:3]:
                score = iv.get("overall_score",0)
                color = SECONDARY if score>=7 else (PRIMARY if score>=5 else ACCENT)
                st.markdown(f"<span style='color:{color}'>● {score:.1f}/10</span> {iv.get('interview_type','')} — {iv.get('created_at','')[:10]}",
                    unsafe_allow_html=True)
    st.stop()

# ── ACTIVE INTERVIEW ───────────────────────────────────────────────────────────
questions   = st.session_state.get("interview_questions",[])
evaluations = st.session_state.get("interview_evaluations",{})
answers     = st.session_state.get("interview_answers",{})
current_q   = st.session_state.get("current_q",0)

# COMPLETE
if st.session_state.get("interview_complete"):
    scores  = [ev.get("score",0) for ev in evaluations.values()]
    overall = sum(scores)/len(scores) if scores else 0

    if not st.session_state.get("interview_final_feedback"):
        with st.spinner("Generating comprehensive feedback..."):
            try:
                final = agent.generate_overall_feedback(scores, career, uid)
                st.session_state["interview_final_feedback"] = final
                db.save_interview(uid,
                    st.session_state.get("interview_type","Technical"),
                    [q.get("question","") for q in questions],
                    [answers.get(i,"") for i in range(len(questions))],
                    {str(i): evaluations.get(i,{}).get("score",0) for i in range(len(questions))},
                    overall, json.dumps(final))
                st.rerun()
            except Exception as e: st.error(f"Error: {e}"); st.stop()

    final = st.session_state.get("interview_final_feedback",{})
    lc = SECONDARY if overall>=7 else (PRIMARY if overall>=5 else ACCENT)
    st.markdown(f"""<div style="background:{BG_CARD};border:2px solid {lc}40;border-radius:20px;
    padding:2rem;text-align:center;margin:1rem 0">
    <div style="font-size:3rem">🎤</div><h2>Interview Complete!</h2>
    <div style="font-size:3.5rem;font-weight:700;color:{lc}">{overall:.1f}<span style="font-size:1.5rem">/10</span></div>
    <div style="color:{lc};font-size:1.2rem;font-weight:600">{final.get('performance_level','')}</div></div>""",
    unsafe_allow_html=True)

    st.markdown(f"> {final.get('overall_feedback','')}")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("**💪 Top Strengths**")
        for s in final.get("top_strengths",[]): st.markdown(f"✅ {s}")
    with col2:
        st.markdown("**📈 Critical Improvements**")
        for i in final.get("critical_improvements",[]): st.markdown(f"📈 {i}")

    st.markdown("**🚀 Next Steps**")
    for step in final.get("next_steps",[]): st.markdown(f"▶️ {step}")
    st.success(f"⏰ **Interview Readiness:** {final.get('readiness_estimate','')}  \n{final.get('encouragement','')}")

    st.markdown("### 📋 Question Breakdown")
    for i,q in enumerate(questions):
        ev    = evaluations.get(i,{})
        score = ev.get("score",0)
        color = SECONDARY if score>=7 else (PRIMARY if score>=5 else ACCENT)
        with st.expander(f"Q{i+1}: {q.get('question','')[:60]}... — {score}/10 {ev.get('verdict','')}"):
            st.markdown(f"**Your answer:** {answers.get(i,'(skipped)')}")
            st.markdown(f"**Feedback:** {ev.get('feedback','')}")
            col1,col2 = st.columns(2)
            with col1:
                for s in ev.get("strengths",[]): st.markdown(f"✅ {s}")
            with col2:
                for imp in ev.get("improvements",[]): st.markdown(f"📈 {imp}")

    if st.button("🔄 Start New Interview", use_container_width=True):
        for k in ["interview_questions","interview_answers","interview_evaluations",
                  "interview_active","interview_complete","interview_final_feedback","current_q"]:
            st.session_state.pop(k, None)
        st.rerun()
    st.stop()

# IN PROGRESS
prog = len(evaluations)/len(questions) if questions else 0
st.progress(prog, text=f"Question {current_q+1} of {len(questions)}")

if current_q < len(questions):
    q    = questions[current_q]
    diff = q.get("difficulty","Medium")
    dc   = SECONDARY if diff=="Easy" else (PRIMARY if diff=="Medium" else ACCENT)

    st.markdown(f"""<div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.25);
    border-radius:16px;padding:1.5rem;margin:1rem 0">
    <div style="color:{TEXT_MUTED};font-size:0.85rem;margin-bottom:0.5rem">
        {q.get('type','')} &nbsp;·&nbsp; <span style="color:{dc}">● {diff}</span>
    </div>
    <h3 style="margin:0">{q.get('question','')}</h3>
    </div>""", unsafe_allow_html=True)

    answer = st.text_area("Your Answer", height=150,
        placeholder="Type your answer here. Think out loud, explain your reasoning...",
        key=f"ans_{current_q}")

    col1,col2 = st.columns(2)
    with col1:
        if st.button("✅ Submit Answer", use_container_width=True):
            ok,err = validate_interview_answer(answer)
            if ok:
                with st.spinner("Evaluating your answer..."):
                    try:
                        ev = agent.evaluate_answer(q.get("question",""), answer, career, uid)
                        st.session_state["interview_answers"][current_q]    = answer
                        st.session_state["interview_evaluations"][current_q] = ev
                        st.session_state["current_q"] = current_q + 1
                        if current_q+1 >= len(questions):
                            st.session_state["interview_complete"] = True
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")
            else: st.warning(err)
    with col2:
        if st.button("⏭️ Skip Question", use_container_width=True):
            st.session_state["current_q"] = current_q + 1
            if current_q+1 >= len(questions):
                st.session_state["interview_complete"] = True
            st.rerun()

    if evaluations:
        st.markdown("### ✅ Previous Answers")
        for qi,ev in evaluations.items():
            sc    = ev.get("score",0)
            color = SECONDARY if sc>=7 else (PRIMARY if sc>=5 else ACCENT)
            with st.expander(f"Q{int(qi)+1}: {questions[int(qi)].get('question','')[:50]}... — {sc}/10"):
                col1,col2 = st.columns(2)
                with col1:
                    for s in ev.get("strengths",[]): st.markdown(f"✅ {s}")
                with col2:
                    for imp in ev.get("improvements",[]): st.markdown(f"📈 {imp}")
                st.caption(ev.get("feedback",""))
