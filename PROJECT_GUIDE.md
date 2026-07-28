# StudyPilot AI Project Guide

This guide explains what the project does, how the files work together, why each component exists, and how data moves through the system.

## 1. Project Purpose

StudyPilot AI is a Streamlit web app that helps a student turn a PDF syllabus or study material into:

- A topic analysis
- A difficulty map of topics
- A personalized study plan
- A multiple-choice quiz
- Quiz evaluation
- Strong-topic and weak-topic feedback
- Revision recommendations

The project uses CrewAI to organize the LLM work into separate agents. Each agent has one clear responsibility, which makes the app easier to understand and easier to improve.

## 2. Big Picture Flow

```text
Student uploads PDF
        |
        v
app.py reads PDF through pdf_processor.py
        |
        v
PDF text is sent to CrewAI tasks
        |
        v
Syllabus Analyzer Agent extracts topics
        |
        v
Study Planner Agent creates schedule
        |
        v
Quiz Generator Agent creates MCQs
        |
        v
Student answers quiz in Streamlit UI
        |
        v
Evaluation Agent checks answers
        |
        v
App shows score, weak topics, and revision advice
```

## 3. File-by-File Explanation

```text
app.py              Main Streamlit app and user interface
agents.py           Defines the AI agents and their roles
tasks.py            Defines the exact work each agent must perform
crew.py             Runs CrewAI workflows and validates outputs
models.py           Pydantic schemas for structured data
pdf_processor.py    Extracts and validates text from uploaded PDFs
requirements.txt    Python dependencies
.env.example        Example environment variables
README.md           Setup and usage instructions
PROJECT_GUIDE.md    Detailed explanation of the project
```

## 4. app.py

`app.py` is the main application file. It controls the Streamlit interface, stores user progress, calls the CrewAI workflow functions, and displays the final results.

### Why this file exists

The project needs a place where the student can interact with the system. Streamlit is used because it lets a Python project become a web app quickly without needing separate frontend code.

### Main imports

```python
import html
import os
from datetime import date

import streamlit as st
from dotenv import load_dotenv
```

These imports support:

- HTML escaping for safe custom UI text
- Environment variable loading
- Date selection for the exam date
- Streamlit UI rendering

The app also imports project-specific functions:

```python
from crew import evaluate_quiz, generate_quiz, generate_study_plan
from models import EvaluationResult, Quiz, StudyPlan, Topic
from pdf_processor import extract_pdf_text, validate_pdf_text
```

This means `app.py` does not directly build agents or parse CrewAI output. It delegates those jobs to smaller files.

### `load_dotenv()`

This loads environment variables from `.env`.

Why it matters:

- API keys should not be hardcoded in Python files.
- The LLM provider can be changed through environment variables.
- The same code can run on different machines with different keys.

### `st.set_page_config(...)`

This sets the Streamlit page title, icon, and layout.

Why it matters:

- The page title identifies the app in the browser.
- Wide layout gives study plans and tables enough room.

### `apply_theme()`

This function injects custom CSS into the Streamlit app.

What it does:

- Defines colors
- Styles the background
- Styles cards, badges, buttons, tabs, metrics, expanders, and progress bars
- Makes the app feel more polished than default Streamlit

Why it exists:

Streamlit works out of the box, but the default look can feel plain. This function gives the app a consistent study-dashboard design.

Important design idea:

The CSS is kept in one function so styling does not get mixed into the app logic everywhere.

### `render_card(title, body)`

This renders a reusable card section.

Used for:

- Quiz introduction
- Evaluation introduction
- Small dashboard-style blocks

Why it exists:

Instead of writing the same HTML block multiple times, the app has one helper for repeated card UI.

### `difficulty_badge(difficulty)`

This converts a difficulty label into a styled HTML badge.

Example:

```text
Easy   -> green badge
Medium -> yellow badge
Hard   -> red badge
```

Why it exists:

Difficulty is important in this app, so it needs to be visually easy to scan.

### `render_topic_badges(topics)`

This counts how many topics are Easy, Medium, and Hard, then displays those counts as badges.

Why it exists:

Before reading the full topic table, the student can quickly understand how challenging the uploaded material is.

### `initialize_state()`

This creates default Streamlit session state values:

```python
{
    "pdf_text": "",
    "pdf_name": "",
    "study_plan": None,
    "quiz": None,
    "evaluation": None,
    "student_answers": {},
}
```

Why it exists:

Streamlit reruns the script whenever a user interacts with the app. Without session state, uploaded text, generated plans, quizzes, and results would disappear after each click.

### `has_api_key()`

This checks whether at least one supported LLM API key exists.

Supported keys:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `AZURE_API_KEY`

Why it exists:

CrewAI needs an LLM provider. If no key is configured, the app warns the user before they try to generate a plan.

### `render_study_plan(plan)`

This displays the generated study plan.

It shows:

- Summary
- Easy/Medium/Hard topic counts
- Daily schedule
- Hours per day
- Difficulty focus
- Topics for each day
- Study tasks
- Topic map table

Why it exists:

The AI output comes back as structured data. This function turns that structure into a readable study dashboard.

### `render_quiz(quiz)`

This displays MCQ questions and answer choices.

For each question, it shows:

- Question text
- Topic badge
- Difficulty badge
- Radio buttons for options

Why it exists:

The quiz must collect one answer for each question in a simple, controlled way. Streamlit radio buttons are a good fit because each MCQ has exactly one correct answer.

### `render_evaluation(evaluation)`

This displays quiz results.

It shows:

- Score
- Percentage progress bar
- Per-question feedback
- Strong topics
- Weak topics
- Revision recommendations

Why it exists:

The purpose of the quiz is not just scoring. The important learning value comes from turning mistakes into a revision plan.

### `main()`

This is the main app workflow.

It does the following:

1. Applies the custom theme.
2. Initializes session state.
3. Shows the hero/header section.
4. Warns if no API key exists.
5. Builds sidebar controls.
6. Displays status metrics.
7. Handles PDF upload and extraction.
8. Creates three tabs: Plan, Quiz, Results.
9. Runs study-plan generation when clicked.
10. Runs quiz generation when clicked.
11. Runs evaluation after answers are submitted.

Why it exists:

`main()` is the single place where the app's user journey is assembled.

## 5. pdf_processor.py

`pdf_processor.py` handles PDF text extraction.

### Why this file exists

The app needs PDF text before an LLM can analyze the material. Keeping PDF logic separate from `app.py` makes the app easier to maintain.

### `extract_pdf_text(uploaded_file)`

This function:

1. Reads the uploaded file bytes.
2. Rejects empty files.
3. Opens the PDF using `pypdf.PdfReader`.
4. Tries to decrypt PDFs with an empty password.
5. Extracts text page by page.
6. Prefixes extracted text with page markers.
7. Returns one combined text string.

Why page markers are useful:

They help preserve the original document structure. The LLM can see where one page ends and another starts.

### Encrypted PDFs

If the PDF is encrypted and cannot be opened, the function raises:

```text
Encrypted PDFs are not supported in this first version.
```

Why:

This keeps version one simple. Handling protected documents adds complexity and can create confusing failures.

### `validate_pdf_text(text, min_chars=200)`

This checks whether extracted PDF text is usable.

It rejects:

- PDFs with no readable text
- PDFs with too little text

Why it exists:

Many scanned PDFs are just images. `pypdf` cannot read image text without OCR. This validation fails early with a useful message instead of sending bad input to the LLM.

## 6. models.py

`models.py` defines the structured data used throughout the project. It uses Pydantic models.

### Why this file exists

LLMs can produce messy text. This app needs reliable structures such as topics, schedules, quiz questions, and evaluation results. Pydantic validates that the AI output has the expected shape.

### `Difficulty`

```python
Difficulty = Literal["Easy", "Medium", "Hard"]
```

This restricts difficulty to exactly three values.

Why:

The UI badges and planning logic depend on consistent labels. If the model returned `simple`, `moderate`, or `difficult`, the app would become harder to render reliably.

### `Topic`

Represents one study topic.

Fields:

- `name`: short topic name
- `category`: broader unit or chapter
- `difficulty`: Easy, Medium, or Hard
- `reason`: why that difficulty was assigned

Why:

The study plan and quiz both depend on a clean topic list.

### `SyllabusAnalysis`

Represents the first AI output.

Fields:

- `summary`
- `topics`

Why:

Before planning, the system needs to understand what the PDF contains.

### `StudyDay`

Represents one day in the study schedule.

Fields:

- `day`
- `focus`
- `topics`
- `difficulty_focus`
- `hours`
- `tasks`

Why:

A study plan needs daily structure, not just a list of topics.

### `StudyPlan`

Represents the full plan.

Fields:

- `summary`
- `topics`
- `schedule`
- `revision_advice`

Why:

This model combines the topic map with the planned schedule and final advice.

### `MCQ`

Represents one multiple-choice question.

Fields:

- `id`
- `topic`
- `difficulty`
- `question`
- `options`
- `correct_answer`
- `explanation`

Validation rules:

- Each MCQ must have exactly 4 options.
- The correct answer cannot be empty.
- The correct answer must exactly match one of the options.

Why:

These rules prevent broken quiz questions from appearing in the UI.

### `Quiz`

Represents a full quiz.

Fields:

- `instructions`
- `questions`

Why:

The app needs one container for all MCQs and quiz-level instructions.

### `QuestionFeedback`

Represents feedback for one answered question.

Fields:

- `question_id`
- `topic`
- `student_answer`
- `correct_answer`
- `is_correct`
- `explanation`

Why:

Students need to know exactly what they got right or wrong and why.

### `EvaluationResult`

Represents the full quiz evaluation.

Fields:

- `score`
- `total_questions`
- `percentage`
- `question_feedback`
- `strong_topics`
- `weak_topics`
- `revision_recommendations`

Why:

The app turns quiz performance into learning guidance.

## 7. agents.py

`agents.py` defines the CrewAI agents.

### Why this file exists

Each agent has a role, goal, and backstory. Separating agents from tasks makes the system easier to reason about:

- Agents define who is doing the work.
- Tasks define what work must be done.

### `get_llm_model()`

This returns the LLM model name from the environment:

```python
os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
```

Why:

The default model works for OpenAI, but the user can switch providers or models from `.env` without editing code.

### `syllabus_analyzer_agent()`

Role:

```text
Syllabus Analyzer Agent
```

Goal:

Extract topics, organize them into categories, and classify difficulty.

Why:

The system cannot build a good plan until it knows what the student needs to study.

### `study_planner_agent()`

Role:

```text
Study Planner Agent
```

Goal:

Create a practical schedule using difficulty, study hours, and exam date.

Why:

Students need a realistic day-by-day plan, not only topic extraction.

### `quiz_generator_agent()`

Role:

```text
Quiz Generator Agent
```

Goal:

Generate MCQs strictly from the uploaded material.

Why:

Practice questions help check understanding. The strict PDF rule reduces hallucinated questions.

### `evaluation_agent()`

Role:

```text
Evaluation Agent
```

Goal:

Evaluate answers, calculate scores, identify strong and weak topics, and recommend revision.

Why:

Feedback is what turns a quiz into a study tool.

### `verbose=True`

All agents use verbose mode.

Why:

This helps during development because CrewAI logs more details about what it is doing.

### `allow_delegation=False`

All agents have delegation disabled.

Why:

This keeps the first version predictable. Each agent does its own assigned task instead of creating additional sub-workflows.

## 8. tasks.py

`tasks.py` defines the task prompts given to the agents.

### Why this file exists

Agents are general workers. Tasks give them exact instructions, rules, context, and expected output format.

### `_shorten_text(text, max_chars=18000)`

This trims long PDF text before sending it to the LLM.

Why:

LLMs have context limits. Very long PDFs can exceed those limits or become expensive and slow. Truncation keeps the demo simple and more reliable.

Tradeoff:

If important content appears after the first 18,000 characters, the model may not see it.

### `create_syllabus_analysis_task(pdf_text)`

This task asks the Syllabus Analyzer Agent to:

- Read the PDF text
- Extract study topics
- Create topic names
- Assign categories
- Classify difficulty
- Explain difficulty
- Write a summary

Output model:

```python
SyllabusAnalysis
```

Why:

This creates the foundation for the rest of the workflow.

### `create_study_plan_task(analysis_task, exam_date, study_hours_per_day)`

This task asks the Study Planner Agent to:

- Use the syllabus analysis from the previous task
- Consider the exam date
- Consider available study hours per day
- Prioritize hard topics earlier
- Include practice and revision
- Return a complete study plan

Output model:

```python
StudyPlan
```

Why:

The plan should be personalized to the student's time and deadline.

Important detail:

This task uses:

```python
context=[analysis_task]
```

That means it receives the output of the syllabus analysis task.

### `create_quiz_task(pdf_text, topics, question_count)`

This task asks the Quiz Generator Agent to:

- Generate a selected number of MCQs
- Use only facts from the PDF
- Cover a mix of difficulties
- Tag each question with a topic
- Create exactly 4 options per question
- Include a correct answer and explanation

Output model:

```python
Quiz
```

Why:

The quiz checks whether the student understands the uploaded material.

### `create_evaluation_task(quiz, student_answers)`

This task asks the Evaluation Agent to:

- Compare student answers with the answer key
- Calculate score
- Calculate percentage
- Mark each question correct or incorrect
- Identify strong topics
- Identify weak topics
- Recommend revision actions

Output model:

```python
EvaluationResult
```

Why:

The final output should help the student decide what to revise next.

## 9. crew.py

`crew.py` runs the CrewAI workflows and converts CrewAI output into validated Pydantic models.

### Why this file exists

The Streamlit app should not know the details of CrewAI output handling. `crew.py` acts as a service layer between the UI and the agent/task system.

### `_model_from_task_output(task, model_class)`

This reads output from a CrewAI task and validates it.

It tries several output formats:

1. `output.pydantic`
2. `output.json_dict`
3. `output.raw`

Why:

CrewAI can return structured output in different forms depending on version and execution. This helper makes the app more robust.

If no usable output exists, it raises a clear runtime error.

### `_run_crew(tasks)`

This builds and runs a CrewAI `Crew`.

Important settings:

```python
process=Process.sequential
```

Why sequential process:

The study plan depends on the syllabus analysis. Sequential execution is easier to understand and safer for a beginner-friendly project.

### `generate_study_plan(pdf_text, exam_date, study_hours_per_day)`

This function:

1. Creates the syllabus analysis task.
2. Creates the study plan task.
3. Runs both tasks in order.
4. Returns a validated `StudyPlan`.

Why:

The UI needs one simple function to call when the user clicks `Generate Study Plan`.

### `generate_quiz(pdf_text, topics, question_count)`

This function:

1. Creates the quiz task.
2. Runs the crew.
3. Returns a validated `Quiz`.

Why:

The quiz depends on both the original PDF text and the topic list created during planning.

### `evaluate_quiz(quiz, student_answers)`

This function:

1. Creates the evaluation task.
2. Runs the crew.
3. Returns a validated `EvaluationResult`.

Why:

The UI needs the final feedback in a predictable structure.

## 10. requirements.txt

This file lists the Python packages required by the project.

### `crewai==1.14.5`

Used to create agents, tasks, and crews.

Why:

CrewAI provides the agentic workflow structure.

### `streamlit==1.37.1`

Used to build the web interface.

Why:

Streamlit makes it fast to build a Python dashboard.

### `pypdf==4.3.1`

Used to extract text from uploaded PDFs.

Why:

The agents need text input, not raw PDF files.

### `pydantic>=2.8.2,<3.0.0`

Used for data validation.

Why:

It keeps LLM output structured and prevents broken data from moving through the app.

### `python-dotenv>=1.2.2,<2.0.0`

Used to load `.env`.

Why:

API keys and model names should be configured outside the code.

## 11. .env.example

This file shows the user how to configure API keys and model names.

Example:

```text
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=openai/gpt-4o-mini
```

Why it exists:

The real `.env` file should stay private. `.env.example` documents what variables are needed without exposing secrets.

## 12. README.md

The README is the quick-start document.

It explains:

- What the project does
- Project structure
- Installation
- Running the app
- How to use it
- Sample input and output
- Troubleshooting

Why it exists:

A user should be able to open the project and run it without reading the entire codebase.

## 13. Data Flow in Detail

### Step 1: User uploads a PDF

In `app.py`, Streamlit receives the uploaded file:

```python
uploaded_pdf = st.file_uploader("Upload syllabus or study-material PDF", type=["pdf"])
```

The app accepts only PDF files.

### Step 2: PDF text is extracted

When a new file is uploaded:

```python
text = extract_pdf_text(uploaded_pdf)
validate_pdf_text(text)
```

The extracted text is stored in:

```python
st.session_state.pdf_text
```

### Step 3: User generates a study plan

When the button is clicked:

```python
generate_study_plan(
    pdf_text=st.session_state.pdf_text,
    exam_date=str(exam_date),
    study_hours_per_day=float(study_hours),
)
```

This triggers two tasks:

1. Analyze syllabus
2. Build study plan

### Step 4: User generates a quiz

The quiz uses:

- The PDF text
- The topics from the study plan
- The selected number of questions

```python
generate_quiz(
    pdf_text=st.session_state.pdf_text,
    topics=st.session_state.study_plan.topics,
    question_count=question_count,
)
```

### Step 5: Student answers questions

Each answer is stored using the question ID:

```python
answers = {
    question.id: st.session_state.get(f"answer_{question.id}")
    for question in st.session_state.quiz.questions
}
```

### Step 6: Quiz is evaluated

The app checks that every question has an answer. Then it calls:

```python
evaluate_quiz(
    quiz=st.session_state.quiz,
    student_answers=answers,
)
```

### Step 7: Results are displayed

The evaluation result is shown in the Results tab.

The student sees:

- Score
- Percentage
- Correct and incorrect answers
- Strong topics
- Weak topics
- Revision recommendations

## 14. Why Agentic AI Is Used Here

This project could have used one giant prompt, but it uses multiple agents instead.

Why multiple agents are better for this project:

- The syllabus analyzer focuses only on understanding the PDF.
- The planner focuses only on building a schedule.
- The quiz generator focuses only on question creation.
- The evaluator focuses only on feedback and revision.

This separation makes the workflow easier to debug and explain.

## 15. Why Pydantic Is Important

LLMs are flexible, but apps need predictable data.

For example, the UI expects:

- Topics to have names and difficulty labels
- MCQs to have exactly 4 options
- Correct answers to match one of the options
- Evaluations to include score and feedback

Pydantic acts like a quality gate. If the AI output is malformed, the app can fail clearly instead of showing broken UI.

## 16. Why Session State Is Important

Streamlit reruns the whole script after interaction.

Without session state:

- The uploaded PDF text would be lost.
- The study plan would disappear after a button click.
- The quiz would reset.
- Evaluation results would not persist.

Session state lets the app feel like a normal interactive web app.

## 17. Current Limitations

This project is a strong first version, but it has some limits.

### No OCR

Scanned PDFs may fail because they contain images instead of selectable text.

Possible improvement:

- Add OCR with tools such as Tesseract or a document AI service.

### Long PDFs are truncated

`tasks.py` only sends the first 18,000 characters of PDF text.

Possible improvement:

- Chunk the PDF
- Summarize sections
- Use retrieval-augmented generation

### No database

The app stores data only in Streamlit session state.

Possible improvement:

- Add SQLite or another database to save study plans, quiz history, and progress.

### No user accounts

The app is currently single-session.

Possible improvement:

- Add authentication if multiple students need persistent profiles.

### AI output can still fail

Even with Pydantic validation, the LLM can sometimes return invalid or incomplete data.

Possible improvement:

- Add retries
- Add stricter repair prompts
- Add fallback parsing

## 18. Possible Future Features

- Save generated study plans
- Export study plan as PDF
- Export quiz results
- Add flashcards
- Add spaced repetition
- Add OCR support
- Add calendar integration
- Add topic progress tracking
- Add charts for weak topics over time
- Add question difficulty balancing controls
- Add multi-PDF support

## 19. How to Run the Project

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your API key.

Run the app:

```powershell
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

## 20. Best Way to Explain This Project in a Presentation

Use this short explanation:

```text
StudyPilot AI is an agentic study assistant built with Streamlit and CrewAI.
The user uploads a study-material PDF. The app extracts text from the PDF,
then multiple AI agents analyze the syllabus, classify topic difficulty,
create a personalized study plan, generate MCQ practice questions, evaluate
the student's answers, and recommend weak-topic revision. Pydantic models
validate the AI outputs so the Streamlit interface can display reliable,
structured results.
```

## 21. Component Summary

| Component | What it does | Why it matters |
| --- | --- | --- |
| Streamlit UI | Lets the user upload PDFs, click buttons, answer quizzes, and view results | Makes the project usable as a web app |
| PDF processor | Extracts text from PDF files | Converts uploaded material into LLM-readable input |
| CrewAI agents | Separate AI roles for analysis, planning, quiz generation, and evaluation | Makes the workflow modular and explainable |
| CrewAI tasks | Give exact instructions and expected outputs to agents | Controls what each agent should produce |
| Pydantic models | Validate topics, plans, quizzes, and evaluations | Keeps data reliable |
| Session state | Stores current PDF, plan, quiz, and evaluation | Prevents data loss during Streamlit reruns |
| Environment variables | Store API keys and model choice | Keeps secrets out of code |

## 22. Simple Mental Model

Think of the project as a study team:

- `pdf_processor.py` reads the book.
- `agents.py` defines the team members.
- `tasks.py` gives each team member instructions.
- `crew.py` manages the team workflow.
- `models.py` checks that the team returns clean forms.
- `app.py` shows everything to the student.

