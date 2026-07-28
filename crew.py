import json
from typing import Any, List

from crewai import Crew, Process, Task
from pydantic import BaseModel

from models import EvaluationResult, Quiz, StudyPlan, Topic
from tasks import (
    create_evaluation_task,
    create_quiz_task,
    create_study_plan_task,
    create_syllabus_analysis_task,
)


def _model_from_task_output(task: Task, model_class: type[BaseModel]) -> BaseModel:
    """Read structured data from a CrewAI task output and validate it with Pydantic."""
    output = task.output

    if output is None:
        raise RuntimeError("CrewAI did not return task output.")

    if getattr(output, "pydantic", None):
        return output.pydantic

    if getattr(output, "json_dict", None):
        return model_class.model_validate(output.json_dict)

    raw = getattr(output, "raw", None)
    if raw:
        try:
            return model_class.model_validate_json(raw)
        except Exception:
            return model_class.model_validate(json.loads(raw))

    raise RuntimeError("CrewAI returned an empty response.")


def _run_crew(tasks: list[Task]) -> Any:
    # A Crew coordinates agents and tasks. Sequential process makes the workflow
    # beginner-friendly: each task runs after its declared context is available.
    crew = Crew(
        agents=[task.agent for task in tasks],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    return crew.kickoff()


def generate_study_plan(
    pdf_text: str,
    exam_date: str,
    study_hours_per_day: float,
) -> StudyPlan:
    analysis_task = create_syllabus_analysis_task(pdf_text)
    plan_task = create_study_plan_task(
        analysis_task=analysis_task,
        exam_date=exam_date,
        study_hours_per_day=study_hours_per_day,
    )

    _run_crew([analysis_task, plan_task])
    return _model_from_task_output(plan_task, StudyPlan)


def generate_quiz(
    pdf_text: str,
    topics: List[Topic],
    question_count: int,
) -> Quiz:
    quiz_task = create_quiz_task(pdf_text, topics, question_count)
    _run_crew([quiz_task])
    return _model_from_task_output(quiz_task, Quiz)


def evaluate_quiz(quiz: Quiz, student_answers: dict[str, str]) -> EvaluationResult:
    evaluation_task = create_evaluation_task(quiz, student_answers)
    _run_crew([evaluation_task])
    return _model_from_task_output(evaluation_task, EvaluationResult)
