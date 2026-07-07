"""
pages/08_🎤_Mock_Interview.py
"""
import streamlit as st
import json
from agents.interview_mentor import InterviewMentorAgent
from database import db
from utils.session import init_session, login_gate, clear_interview_state
from utils.validators import validate_interview_answer
from utils.exporters import interview_to_markdown
from config.constants import INTERVIEW_TYPES, INTERVIEW_DIFFICULTY
from utils.ui_components import (apply_styles, page_header, score_gauge,
                                  PRIMARY, SECONDARY, ACCENT, TEXT_MUTED, BG_CARD)

def render():
    init_session()
    apply_styles()
    page_header("Mock Interview", "Practice with AI and get detailed feedback",
                "Interview Mentor Agent")

    if not login_gate("Mock Interview"):
        return

    uid = st.session_state.user_id
    user = db.get_user(uid)
    career = user.get("dream_career", "Software Engineer")
    agent = InterviewMentorAgent()

    # Setup
    col1, col2, col3 = st.columns(3)
    with col1:
        interview_type = st.selectbox("Interview Type", INTERVIEW_TYPES)
    with col2:
        difficulty = st.selectbox("Difficulty", INTERVIEW_DIFFICULTY)
    with col3:
        num_questions = st.selectbox("Number of Questions", [3, 5, 7, 10], index=1)

    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🎤 Start Mock Interview", use_container_width=True)
    with col2:
        if st.button("📊 View Past Interviews", use_container_width=True):
            st.session_state["show_past"] = not st.session_state.get("show_past", False)

    # ── Past interviews ───────────────────────────────────────────────────────
    if st.session_state.get("show_past"):
        past = db.get_interviews(uid)
        if past:
            st.markdown("### 📊 Interview History")
            for interview in past:
                score = interview.get("overall_score", 0)
                color = SECONDARY if score >= 7 else (PRIMARY if score >= 5 else ACCENT)
                st.markdown(f"""
                <div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.2);
                border-radius:12px;padding:1rem;margin:0.5rem 0;
                display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <strong>{interview.get('interview_type','Interview')}</strong>
                        <div style="color:{TEXT_MUTED};font-size:0.8rem">{interview.get('created_at','')[:10]}</div>
                    </div>
                    <div style="color:{color};font-size:1.5rem;font-weight:700">
                        {score:.1f}/10
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No past interviews yet. Start one above!")

    # ── Start interview ───────────────────────────────────────────────────────
    if start_btn or st.session_state.get("interview_active"):
        if start_btn:
            # Generate questions
            with st.spinner("Interview Mentor Agent is preparing your questions..."):
                try:
                    questions = agent.generate_questions(
                        career, interview_type, difficulty, uid)[:num_questions]
                    st.session_state["interview_questions"] = questions
                    st.session_state["interview_answers"] = {}
                    st.session_state["interview_evaluations"] = {}
                    st.session_state["interview_active"] = True
                    st.session_state["interview_type"] = interview_type
                    st.session_state["current_q"] = 0
                    st.session_state["interview_complete"] = False
                except Exception as e:
                    st.error(f"Error generating questions: {e}")
                    return

        questions = st.session_state.get("interview_questions",[])
        if not questions:
            st.error("No questions generated. Please try again.")
            return

        if st.session_state.get("interview_complete"):
            # Show final results
            _show_results(uid, career, agent)
            return

        current_q = st.session_state.get("current_q", 0)
        evaluations = st.session_state.get("interview_evaluations", {})

        # Progress bar
        progress = len(evaluations) / len(questions)
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05);border-radius:100px;height:6px;margin:1rem 0">
            <div style="background:linear-gradient(90deg,{PRIMARY},{SECONDARY});
            width:{progress*100}%;height:100%;border-radius:100px;transition:width 0.5s"></div>
        </div>
        <div style="color:{TEXT_MUTED};font-size:0.85rem;margin-bottom:1rem">
            Question {min(current_q+1, len(questions))} of {len(questions)}
        </div>
        """, unsafe_allow_html=True)

        if current_q < len(questions):
            q = questions[current_q]
            diff = q.get("difficulty","Medium")
            diff_color = SECONDARY if diff=="Easy" else (PRIMARY if diff=="Medium" else ACCENT)

            st.markdown(f"""
            <div style="background:{BG_CARD};border:1px solid rgba(108,99,255,0.25);
            border-radius:16px;padding:1.5rem;margin:1rem 0">
                <div style="display:flex;justify-content:space-between;margin-bottom:1rem">
                    <span style="color:{TEXT_MUTED};font-size:0.85rem">
                        {q.get('type','Technical')} · 
                        <span style="color:{diff_color}">●</span> {diff}
                    </span>
                    <span style="color:{TEXT_MUTED};font-size:0.85rem">Q{current_q+1}</span>
                </div>
                <h3 style="margin:0;font-size:1.1rem">{q.get('question','')}</h3>
                {f'<p style="color:{TEXT_MUTED};font-size:0.85rem;margin-top:0.5rem">Follow-up: {q.get("follow_up","")}</p>' if q.get("follow_up") else ''}
            </div>
            """, unsafe_allow_html=True)

            answer_key = f"answer_{current_q}"
            answer = st.text_area(
                "Your Answer",
                key=answer_key,
                height=150,
                placeholder="Type your answer here... Think out loud, explain your reasoning..."
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Submit Answer", use_container_width=True):
                    valid, err = validate_interview_answer(answer)
                    if valid:
                        with st.spinner("Evaluating your answer..."):
                            try:
                                eval_result = agent.evaluate_answer(
                                    q.get("question",""), answer, career, uid)
                                st.session_state["interview_answers"][current_q] = answer
                                st.session_state["interview_evaluations"][current_q] = eval_result
                                st.session_state["current_q"] = current_q + 1
                                if current_q + 1 >= len(questions):
                                    st.session_state["interview_complete"] = True
                                st.rerun()
                            except Exception as e:
                                st.error(f"Evaluation error: {e}")
                    else:
                        st.warning(err)

            with col2:
                if st.button("⏭️ Skip Question", use_container_width=True):
                    st.session_state["current_q"] = current_q + 1
                    if current_q + 1 >= len(questions):
                        st.session_state["interview_complete"] = True
                    st.rerun()

            # Show previous evaluations
            if evaluations:
                st.markdown("---")
                st.markdown("### 📝 Previous Answers")
                for i, (qidx, ev) in enumerate(evaluations.items()):
                    score = ev.get("score", 0)
                    color = SECONDARY if score >= 7 else (PRIMARY if score >= 5 else ACCENT)
                    verdict = ev.get("verdict","")
                    with st.expander(f"Q{int(qidx)+1}: {questions[int(qidx)].get('question','')[:50]}... — {score}/10"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Score:** <span style='color:{color}'>{score}/10 — {verdict}</span>",
                                       unsafe_allow_html=True)
                            st.markdown("**Strengths:**")
                            for s in ev.get("strengths",[]):
                                st.markdown(f"✅ {s}")
                        with col2:
                            st.markdown("**To Improve:**")
                            for imp in ev.get("improvements",[]):
                                st.markdown(f"📈 {imp}")
                        st.markdown(f"*{ev.get('feedback','')}*")

def _show_results(uid, career, agent):
    questions = st.session_state.get("interview_questions",[])
    answers = st.session_state.get("interview_answers",{})
    evaluations = st.session_state.get("interview_evaluations",{})

    scores = [ev.get("score",0) for ev in evaluations.values()]
    overall = sum(scores) / len(scores) if scores else 0

    # Generate overall feedback
    if "interview_final_feedback" not in st.session_state:
        agent_inst = agent
        with st.spinner("Generating comprehensive feedback..."):
            try:
                final = agent_inst.generate_overall_feedback(scores, career, uid)
                st.session_state["interview_final_feedback"] = final
                # Save to DB
                db.save_interview(
                    uid,
                    st.session_state.get("interview_type","Technical"),
                    [q.get("question","") for q in questions],
                    [answers.get(i,"") for i in range(len(questions))],
                    {str(i): evaluations.get(i,{}).get("score",0) for i in range(len(questions))},
                    overall,
                    json.dumps(final)
                )
            except Exception as e:
                st.error(f"Error: {e}")
                final = {}
    else:
        final = st.session_state.get("interview_final_feedback",{})

    # Results header
    perf_level = final.get("performance_level","Average")
    level_colors = {"Excellent":SECONDARY,"Good":PRIMARY,"Average":"#FFB84D","Needs Improvement":ACCENT}
    lc = level_colors.get(perf_level, PRIMARY)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(108,99,255,0.15),rgba(0,212,170,0.08));
    border:2px solid {lc}40;border-radius:20px;padding:2rem;text-align:center;margin:1rem 0">
        <div style="font-size:3rem">🎤</div>
        <h2 style="margin:0.5rem 0">Interview Complete!</h2>
        <div style="font-size:3rem;font-weight:700;color:{lc}">{overall:.1f}<span style="font-size:1.5rem">/10</span></div>
        <div style="color:{lc};font-size:1.2rem;font-weight:600">{perf_level}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1,2])
    with col1:
        st.plotly_chart(score_gauge(overall*10, "Performance"), use_container_width=True)
    with col2:
        st.markdown("**Overall Feedback:**")
        st.markdown(f"> {final.get('overall_feedback','')}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**💪 Top Strengths:**")
            for s in final.get("top_strengths",[]):
                st.markdown(f"✅ {s}")
        with col_b:
            st.markdown("**📈 Critical Improvements:**")
            for imp in final.get("critical_improvements",[]):
                st.markdown(f"📈 {imp}")

    st.markdown("### 🚀 Next Steps")
    for step in final.get("next_steps",[]):
        st.markdown(f"▶️ {step}")

    st.markdown(f"""
    <div style="background:rgba(0,212,170,0.08);border:1px solid rgba(0,212,170,0.2);
    border-radius:12px;padding:1rem;margin-top:1rem">
        <strong>⏰ Interview Readiness:</strong> {final.get('readiness_estimate','')}<br>
        <em style="color:{SECONDARY}">{final.get('encouragement','')}</em>
    </div>
    """, unsafe_allow_html=True)

    # Question-by-question breakdown
    st.markdown("### 📋 Question Breakdown")
    for i, q in enumerate(questions):
        ev = evaluations.get(i,{})
        score = ev.get("score",0)
        color = SECONDARY if score>=7 else (PRIMARY if score>=5 else ACCENT)
        with st.expander(f"Q{i+1}: {q.get('question','')[:60]}... — {score}/10"):
            st.markdown(f"**Your Answer:** {answers.get(i,'(skipped)')}")
            st.markdown(f"**Score:** <span style='color:{color}'>{score}/10 — {ev.get('verdict','')}</span>",
                       unsafe_allow_html=True)
            st.markdown(f"**Feedback:** {ev.get('feedback','')}")
            col1, col2 = st.columns(2)
            with col1:
                for s in ev.get("strengths",[]):
                    st.markdown(f"✅ {s}")
            with col2:
                for imp in ev.get("improvements",[]):
                    st.markdown(f"📈 {imp}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Interview", use_container_width=True):
            clear_interview_state()
            st.session_state.pop("interview_final_feedback", None)
            st.rerun()
    with col2:
        if st.button("📈 View Progress Dashboard", use_container_width=True):
            st.switch_page("pages/09_📈_Progress_Dashboard.py")


if __name__ == "__main__":
    from utils.sidebar import render_sidebar
    render_sidebar()
    render()
