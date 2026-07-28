import os

from crewai import Agent


def get_llm_model() -> str:
    """CrewAI uses LiteLLM model names, for example openai/gpt-4o-mini."""
    return os.getenv("LLM_MODEL", "openai/gpt-4o-mini")


def syllabus_analyzer_agent() -> Agent:
    return Agent(
        role="Syllabus Analyzer Agent",
        goal=(
            "Extract study topics from uploaded PDF text, organize them into "
            "clear categories, and classify each topic as Easy, Medium, or Hard."
        ),
        backstory=(
            "You are a careful academic assistant who reads syllabi and study "
            "material like a teacher preparing a course map for students."
        ),
        llm=get_llm_model(),
        verbose=True,
        allow_delegation=False,
    )


def study_planner_agent() -> Agent:
    return Agent(
        role="Study Planner Agent",
        goal=(
            "Create practical study schedules from topic difficulty, available "
            "study hours per day, and the exam date."
        ),
        backstory=(
            "You are a student success coach who balances ambition with realistic "
            "daily workload and revision time."
        ),
        llm=get_llm_model(),
        verbose=True,
        allow_delegation=False,
    )


def quiz_generator_agent() -> Agent:
    return Agent(
        role="Quiz Generator Agent",
        goal=(
            "Generate high-quality MCQs strictly from the uploaded study material, "
            "with correct answers and short explanations."
        ),
        backstory=(
            "You are an exam setter who never asks questions outside the provided "
            "material and always writes plausible answer options."
        ),
        llm=get_llm_model(),
        verbose=True,
        allow_delegation=False,
    )


def evaluation_agent() -> Agent:
    return Agent(
        role="Evaluation Agent",
        goal=(
            "Evaluate student quiz answers, calculate the score, identify strong "
            "and weak topics, and recommend targeted revision."
        ),
        backstory=(
            "You are a supportive tutor who turns quiz results into specific, "
            "actionable revision advice."
        ),
        llm=get_llm_model(),
        verbose=True,
        allow_delegation=False,
    )
