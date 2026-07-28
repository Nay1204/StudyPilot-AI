from typing import List, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


Difficulty = Literal["Easy", "Medium", "Hard"]


class Topic(BaseModel):
    name: str = Field(..., description="Short topic name")
    category: str = Field(..., description="Broader unit, chapter, or category")
    difficulty: Difficulty
    reason: str = Field(..., description="Why this difficulty was assigned")


class SyllabusAnalysis(BaseModel):
    summary: str
    topics: List[Topic] = Field(..., min_length=1)


class StudyDay(BaseModel):
    day: str = Field(..., description="Day label or date")
    focus: str
    topics: List[str] = Field(..., min_length=1)
    difficulty_focus: str
    hours: float = Field(..., gt=0)
    tasks: List[str] = Field(..., min_length=1)


class StudyPlan(BaseModel):
    summary: str
    topics: List[Topic] = Field(..., min_length=1)
    schedule: List[StudyDay] = Field(..., min_length=1)
    revision_advice: List[str] = Field(..., min_length=1)


class MCQ(BaseModel):
    id: str
    topic: str
    difficulty: Difficulty
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

    @field_validator("options")
    @classmethod
    def require_four_options(cls, options: List[str]) -> List[str]:
        if len(options) != 4:
            raise ValueError("Each MCQ must contain exactly 4 options.")
        return options

    @field_validator("correct_answer")
    @classmethod
    def answer_must_not_be_empty(cls, answer: str) -> str:
        if not answer.strip():
            raise ValueError("Correct answer cannot be empty.")
        return answer

    @model_validator(mode="after")
    def correct_answer_must_match_option(self) -> "MCQ":
        if self.correct_answer not in self.options:
            raise ValueError("Correct answer must exactly match one of the options.")
        return self


class Quiz(BaseModel):
    instructions: str
    questions: List[MCQ] = Field(..., min_length=1)


class QuestionFeedback(BaseModel):
    question_id: str
    topic: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str


class EvaluationResult(BaseModel):
    score: int = Field(..., ge=0)
    total_questions: int = Field(..., gt=0)
    percentage: float = Field(..., ge=0, le=100)
    question_feedback: List[QuestionFeedback] = Field(..., min_length=1)
    strong_topics: List[str]
    weak_topics: List[str]
    revision_recommendations: List[str] = Field(..., min_length=1)
