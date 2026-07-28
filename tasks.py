import json
from typing import List

from crewai import Task

from agents import (
    evaluation_agent,
    quiz_generator_agent,
    study_planner_agent,
    syllabus_analyzer_agent,
)
from models import EvaluationResult, Quiz, StudyPlan, SyllabusAnalysis, Topic


def _shorten_text(text: str, max_chars: int = 18000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[Text truncated to fit the LLM context window.]"


def create_syllabus_analysis_task(pdf_text: str) -> Task:
    return Task(
        description=f"""
Read the study material below and extract the syllabus or study topics.

Rules:
- Use only the provided PDF text.
- Create clear topic names.
- Assign each topic a category.
- Classify difficulty as exactly one of: Easy, Medium, Hard.
- Explain the difficulty classification briefly.
- Include a concise overall summary.

PDF TEXT:
{_shorten_text(pdf_text)}
""",
        expected_output=(
            "A JSON object with a summary and a list of categorized topics with "
            "difficulty labels."
        ),
        agent=syllabus_analyzer_agent(),
        output_json=SyllabusAnalysis,
    )


def create_study_plan_task(
    analysis_task: Task,
    exam_date: str,
    study_hours_per_day: float,
) -> Task:
    return Task(
        description=f"""
Create a personalized study plan using the syllabus analysis from the previous task.

Student constraints:
- Exam date: {exam_date}
- Available study hours per day: {study_hours_per_day}

Rules:
- Prioritize Hard topics earlier and revisit them.
- Include Easy, Medium, and Hard topics where available.
- Keep each day realistic for the available hours.
- Include active recall, practice, and revision tasks.
- The final output must include the analyzed topics and the schedule.
""",
        expected_output=(
            "A JSON object containing summary, topics, daily schedule, and final "
            "revision advice."
        ),
        agent=study_planner_agent(),
        context=[analysis_task],
        output_json=StudyPlan,
    )


def create_quiz_task(pdf_text: str, topics: List[Topic], question_count: int) -> Task:
    topics_json = json.dumps([topic.model_dump() for topic in topics], indent=2)
    return Task(
        description=f"""
Generate {question_count} multiple-choice questions from the uploaded PDF text.

Rules:
- Use only facts found in the PDF text.
- Cover a mix of Easy, Medium, and Hard questions.
- Use the topic list to tag each question.
- Each question must have exactly 4 options.
- The correct answer must be one of the options exactly.
- Include a concise explanation grounded in the material.

TOPICS:
{topics_json}

PDF TEXT:
{_shorten_text(pdf_text)}
""",
        expected_output=(
            "A JSON quiz with instructions and MCQs. Each MCQ has id, topic, "
            "difficulty, question, four options, correct answer, and explanation."
        ),
        agent=quiz_generator_agent(),
        output_json=Quiz,
    )


def create_evaluation_task(quiz: Quiz, student_answers: dict[str, str]) -> Task:
    return Task(
        description=f"""
Evaluate the student's answers against the answer key.

Rules:
- Calculate score and percentage.
- Mark each question as correct or incorrect.
- Identify strong topics from correct answers.
- Identify weak topics from incorrect answers.
- Recommend specific topics and actions for revision.
- Be encouraging but accurate.

QUIZ:
{quiz.model_dump_json(indent=2)}

STUDENT ANSWERS:
{json.dumps(student_answers, indent=2)}
""",
        expected_output=(
            "A JSON evaluation containing score, total questions, percentage, "
            "question feedback, strong topics, weak topics, and revision recommendations."
        ),
        agent=evaluation_agent(),
        output_json=EvaluationResult,
    )
