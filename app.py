import html
import os
from datetime import date

import streamlit as st
from dotenv import load_dotenv

from crew import evaluate_quiz, generate_quiz, generate_study_plan
from models import EvaluationResult, Quiz, StudyPlan, Topic
from pdf_processor import extract_pdf_text, validate_pdf_text


load_dotenv()


st.set_page_config(
    page_title="Agentic AI Study & Quiz Assistant",
    page_icon=":books:",
    layout="wide",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #faf7f2;
            --surface: #ffffff;
            --surface-soft: #f7f5fb;
            --text: #24212b;
            --muted: #6f6a7c;
            --border: #e8e2ee;
            --lavender: #8f7cc3;
            --lavender-soft: #eee9fb;
            --blue: #6f9fcf;
            --blue-soft: #e8f1fb;
            --green-soft: #eaf6ef;
            --green: #39745d;
            --red-soft: #faecec;
            --red: #9b4d55;
            --shadow: 0 14px 38px rgba(89, 73, 116, 0.09);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(143, 124, 195, 0.12), transparent 34rem),
                radial-gradient(circle at top right, rgba(111, 159, 207, 0.11), transparent 30rem),
                var(--bg);
            color: var(--text);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.25rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.72);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--text);
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--text);
        }

        h1 {
            font-size: 2.25rem;
            font-weight: 760;
            margin-bottom: 0.35rem;
        }

        h2, h3 {
            font-weight: 700;
        }

        p, li, label, .stMarkdown {
            color: var(--text);
        }

        .hero {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow);
            padding: 1.45rem 1.55rem;
            margin-bottom: 1.15rem;
        }

        .hero-kicker {
            color: var(--lavender);
            font-size: 0.78rem;
            font-weight: 760;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .hero-copy {
            color: var(--muted);
            font-size: 1.03rem;
            line-height: 1.62;
            max-width: 780px;
            margin: 0.35rem 0 0;
        }

        .dashboard-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow);
            padding: 1.15rem 1.2rem;
            margin: 0.85rem 0 1rem;
        }

        .section-title {
            font-size: 1.03rem;
            font-weight: 740;
            margin-bottom: 0.4rem;
        }

        .section-copy {
            color: var(--muted);
            line-height: 1.58;
            margin-bottom: 0.1rem;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.45rem 0 0.25rem;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.22rem 0.62rem;
            font-size: 0.78rem;
            font-weight: 680;
            border: 1px solid transparent;
        }

        .badge-easy {
            color: var(--green);
            background: var(--green-soft);
            border-color: #d4ebdd;
        }

        .badge-medium {
            color: #76613f;
            background: #f8f1df;
            border-color: #ecdfbd;
        }

        .badge-hard {
            color: var(--red);
            background: var(--red-soft);
            border-color: #efd5d8;
        }

        .badge-blue {
            color: #426f9b;
            background: var(--blue-soft);
            border-color: #d5e6f6;
        }

        .badge-lavender {
            color: #68559f;
            background: var(--lavender-soft);
            border-color: #ddd4f3;
        }

        div.stButton > button,
        div.stDownloadButton > button {
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text);
            box-shadow: 0 8px 22px rgba(89, 73, 116, 0.08);
            font-weight: 700;
            min-height: 2.75rem;
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--lavender), var(--blue));
            border: 0;
            color: white;
        }

        div.stButton > button:hover {
            border-color: var(--lavender);
            color: var(--text);
        }

        div.stButton > button[kind="primary"]:hover {
            color: white;
            filter: brightness(0.98);
        }

        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            box-shadow: var(--shadow);
        }

        [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(89, 73, 116, 0.06);
            overflow: hidden;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1.25rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            color: var(--muted);
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: var(--lavender-soft);
            color: var(--text);
        }

        .stTabs [data-testid="stVerticalBlock"] {
            padding-top: 0.35rem;
        }

        [data-testid="stDataFrame"],
        [data-testid="stFileUploader"] {
            border-radius: 8px;
        }

        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--lavender), var(--blue));
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_card(title: str, body: str = "") -> None:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="section-title">{html.escape(title)}</div>
            <div class="section-copy">{html.escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def difficulty_badge(difficulty: str) -> str:
    css_class = {
        "Easy": "badge-easy",
        "Medium": "badge-medium",
        "Hard": "badge-hard",
    }.get(difficulty, "badge-lavender")
    return f'<span class="badge {css_class}">{html.escape(difficulty)}</span>'


def render_topic_badges(topics: list[Topic]) -> None:
    counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    for topic in topics:
        counts[topic.difficulty] += 1

    badges = "".join(
        f'<span class="badge {css_class}">{label}: {counts[label]}</span>'
        for label, css_class in [
            ("Easy", "badge-easy"),
            ("Medium", "badge-medium"),
            ("Hard", "badge-hard"),
        ]
    )
    st.markdown(f'<div class="badge-row">{badges}</div>', unsafe_allow_html=True)


def initialize_state() -> None:
    defaults = {
        "pdf_text": "",
        "pdf_name": "",
        "study_plan": None,
        "quiz": None,
        "evaluation": None,
        "student_answers": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def has_api_key() -> bool:
    provider_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "AZURE_API_KEY",
    ]
    return any(os.getenv(key) for key in provider_keys)


def render_study_plan(plan: StudyPlan) -> None:
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="section-title">Study Plan</div>
            <div class="section-copy">{html.escape(plan.summary)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_topic_badges(plan.topics)

    for day in plan.schedule:
        with st.expander(f"{day.day}: {day.focus}", expanded=True):
            st.markdown(
                f"""
                <div class="badge-row">
                    <span class="badge badge-blue">{day.hours} hour(s)</span>
                    <span class="badge badge-lavender">{html.escape(day.difficulty_focus)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("**Topics:** " + ", ".join(day.topics))
            st.write("**Tasks:**")
            for task in day.tasks:
                st.write(f"- {task}")

    st.subheader("Topic Map")
    topic_rows = [
        {
            "Topic": topic.name,
            "Difficulty": topic.difficulty,
            "Category": topic.category,
            "Reason": topic.reason,
        }
        for topic in plan.topics
    ]
    st.dataframe(topic_rows, use_container_width=True, hide_index=True)


def render_quiz(quiz: Quiz) -> None:
    render_card("Quiz", quiz.instructions)

    for index, question in enumerate(quiz.questions, start=1):
        st.markdown(f"**{index}. {question.question}**")
        st.markdown(
            f"""
            <div class="badge-row">
                <span class="badge badge-blue">{html.escape(question.topic)}</span>
                {difficulty_badge(question.difficulty)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.radio(
            "Choose one answer",
            options=question.options,
            key=f"answer_{question.id}",
            index=None,
        )


def render_evaluation(evaluation: EvaluationResult) -> None:
    render_card("Evaluation", "Your answers have been checked and converted into revision priorities.")
    st.metric("Quiz Score", f"{evaluation.score}/{evaluation.total_questions}")
    st.progress(evaluation.percentage / 100)
    st.write(f"**Percentage:** {evaluation.percentage:.1f}%")

    st.subheader("Question Feedback")
    for item in evaluation.question_feedback:
        status = "Correct" if item.is_correct else "Needs review"
        with st.expander(f"{item.question_id}: {status}"):
            st.write(f"**Your answer:** {item.student_answer}")
            st.write(f"**Correct answer:** {item.correct_answer}")
            st.write(f"**Explanation:** {item.explanation}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Strong Topics")
        if evaluation.strong_topics:
            for topic in evaluation.strong_topics:
                st.success(topic)
        else:
            st.info("No strong topics identified yet.")

    with col2:
        st.subheader("Weak Topics")
        if evaluation.weak_topics:
            for topic in evaluation.weak_topics:
                st.error(topic)
        else:
            st.success("No weak topics identified.")

    st.subheader("Revision Recommendations")
    for recommendation in evaluation.revision_recommendations:
        st.write(f"- {recommendation}")


def main() -> None:
    apply_theme()
    initialize_state()

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">CrewAI study dashboard</div>
            <h1>Agentic AI Study & Quiz Assistant</h1>
            <p class="hero-copy">
                Upload study material, generate a focused study plan, practice with
                MCQs, and get targeted revision recommendations from a team of AI agents.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not has_api_key():
        st.warning(
            "No LLM API key was found. Add one to your .env file before running the agents."
        )

    with st.sidebar:
        st.header("Study Setup")
        uploaded_pdf = st.file_uploader("Upload syllabus or study-material PDF", type=["pdf"])
        exam_date = st.date_input("Exam date", min_value=date.today())
        study_hours = st.number_input(
            "Available study hours per day",
            min_value=0.5,
            max_value=16.0,
            value=2.0,
            step=0.5,
        )
        question_count = st.slider("Number of quiz questions", 3, 15, 6)

    status_cols = st.columns(4)
    with status_cols[0]:
        st.metric("Material", "Loaded" if st.session_state.pdf_text else "Waiting")
    with status_cols[1]:
        st.metric("Plan", "Ready" if st.session_state.study_plan else "Not yet")
    with status_cols[2]:
        st.metric("Quiz", "Ready" if st.session_state.quiz else "Not yet")
    with status_cols[3]:
        st.metric("Review", "Done" if st.session_state.evaluation else "Pending")

    if uploaded_pdf is not None:
        if uploaded_pdf.name != st.session_state.pdf_name:
            try:
                text = extract_pdf_text(uploaded_pdf)
                validate_pdf_text(text)
                st.session_state.pdf_text = text
                st.session_state.pdf_name = uploaded_pdf.name
                st.session_state.study_plan = None
                st.session_state.quiz = None
                st.session_state.evaluation = None
                st.success(f"Loaded {uploaded_pdf.name}")
            except Exception as exc:
                st.session_state.pdf_text = ""
                st.error(f"Could not read the PDF: {exc}")

    tab_plan, tab_quiz, tab_results = st.tabs(["Plan", "Quiz", "Results"])

    with tab_plan:
        generate_plan_clicked = st.button(
            "Generate Study Plan",
            type="primary",
            disabled=not st.session_state.pdf_text,
        )

        if generate_plan_clicked:
            try:
                with st.spinner("CrewAI agents are analyzing the PDF and planning your schedule..."):
                    st.session_state.study_plan = generate_study_plan(
                        pdf_text=st.session_state.pdf_text,
                        exam_date=str(exam_date),
                        study_hours_per_day=float(study_hours),
                    )
                    st.session_state.quiz = None
                    st.session_state.evaluation = None
                st.success("Study plan generated.")
            except Exception as exc:
                st.error(f"Study plan generation failed: {exc}")

        if st.session_state.study_plan:
            render_study_plan(st.session_state.study_plan)

    with tab_quiz:
        if st.session_state.study_plan:
            quiz_clicked = st.button("Generate Quiz")
            if quiz_clicked:
                try:
                    with st.spinner("Quiz Generator Agent is writing MCQs from the PDF..."):
                        st.session_state.quiz = generate_quiz(
                            pdf_text=st.session_state.pdf_text,
                            topics=st.session_state.study_plan.topics,
                            question_count=question_count,
                        )
                        st.session_state.evaluation = None
                    st.success("Quiz generated.")
                except Exception as exc:
                    st.error(f"Quiz generation failed: {exc}")
        else:
            st.info("Generate a study plan first, then create a quiz.")

        if st.session_state.quiz:
            render_quiz(st.session_state.quiz)

            if st.button("Submit Answers", type="primary"):
                answers = {
                    question.id: st.session_state.get(f"answer_{question.id}")
                    for question in st.session_state.quiz.questions
                }
                unanswered = [qid for qid, answer in answers.items() if not answer]
                if unanswered:
                    st.warning("Please answer every question before submitting.")
                else:
                    try:
                        with st.spinner("Evaluation Agent is checking answers and finding weak topics..."):
                            st.session_state.evaluation = evaluate_quiz(
                                quiz=st.session_state.quiz,
                                student_answers=answers,
                            )
                        st.success("Evaluation complete.")
                    except Exception as exc:
                        st.error(f"Evaluation failed: {exc}")

    with tab_results:
        if st.session_state.evaluation:
            render_evaluation(st.session_state.evaluation)
        else:
            st.info("Submit a quiz to see your score and weak-topic analysis.")


if __name__ == "__main__":
    main()
