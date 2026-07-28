# Agentic AI Study & Quiz Assistant using CrewAI

This is a complete beginner-friendly mini-project where a student uploads a syllabus or study-material PDF and CrewAI agents collaborate to:

- Analyze topics from the PDF
- Classify topics as Easy, Medium, or Hard
- Build a personalized study schedule
- Generate MCQs from the uploaded material
- Evaluate answers
- Identify weak topics and recommend revision

## Project Structure

```text
project/
+-- app.py
+-- agents.py
+-- tasks.py
+-- crew.py
+-- pdf_processor.py
+-- models.py
+-- requirements.txt
+-- .env.example
+-- README.md
```

## Agentic Workflow

```text
PDF
-> Syllabus Analyzer Agent
-> Study Planner Agent
-> Quiz Generator Agent
-> Student Answers
-> Evaluation Agent
-> Weak Topics
-> Personalized Revision Recommendations
```

## Requirements

- Python 3.10 or 3.11 recommended
- An LLM API key, such as OpenAI, Anthropic, or Gemini

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and add your API key:

```text
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=openai/gpt-4o-mini
```

## Run the App

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## How to Use

1. Upload a text-based PDF syllabus or study material.
2. Select your exam date.
3. Enter available study hours per day.
4. Click **Generate Study Plan**.
5. Review the schedule and topic difficulty table.
6. Click **Generate Quiz**.
7. Answer every MCQ.
8. Click **Submit Answers**.
9. Review score, weak topics, and revision recommendations.

## Sample Input

Example PDF content:

```text
Introduction to Database Systems
Topics: relational model, keys, normalization, SQL queries, joins,
transactions, ACID properties, indexing, query optimization.
Exam focus: normalization, SQL joins, transaction isolation, indexes.
```

Example student settings:

```text
Exam date: 2026-08-10
Available study hours per day: 2
Quiz questions: 6
```

## Sample Output

Study plan excerpt:

```text
Day 1: Relational model and keys
Estimated time: 2 hours
Tasks:
- Review entity, attribute, relation, tuple, and key definitions.
- Create flashcards for primary keys and foreign keys.
- Solve 5 short SQL schema identification questions.
```

Quiz excerpt:

```text
Question: Which property of a transaction ensures that all operations complete or none do?
Options:
1. Isolation
2. Atomicity
3. Durability
4. Consistency
Correct answer: Atomicity
Explanation: Atomicity means a transaction is treated as one complete unit.
```

Evaluation excerpt:

```text
Score: 4/6
Weak topics:
- Transaction isolation
- Indexing

Revision recommendations:
- Re-read the transaction section and compare ACID properties in a table.
- Practice identifying when an index improves query performance.
```

## Notes

- MCQs are instructed to come strictly from the uploaded PDF text.
- This first version does not use a database.
- This project does not train models and does not use GANs.
- Scanned image PDFs may fail because they do not contain extractable text.

## Troubleshooting

If you see an API key error, check that `.env` exists and contains a valid key.

If PDF extraction fails, try a text-based PDF. Scanned PDFs require OCR, which is intentionally not included to keep this first version simple.

If CrewAI returns invalid structured output, run the action again or reduce the number of quiz questions. Very long PDFs are truncated before being sent to the LLM to keep the demo simple and reliable.
