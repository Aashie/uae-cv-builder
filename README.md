# UAE CV Builder

An evidence-based Python resume/career intelligence platform for UAE job seekers. It takes a candidate profile and job description, extracts evidence, matches skills, scores fit, identifies gaps, generates safe resume sections, validates final resume structure, and exports a DOCX resume through a Streamlit demo.

This project follows a no-invention rule. It may rewrite, structure, categorize, validate, and export candidate-provided data, but it must not invent skills, achievements, job titles, credentials, education, tools, or experience.

## Features

- Candidate profile + job description analysis
- Evidence extraction
- Skill matching
- Gap analysis
- Career recommendations
- Skills section generation
- Final resume assembly
- Final resume schema validation
- Export adapter
- DOCX export
- Streamlit demo UI
- Failure-safe orchestrator that preserves partial outputs

## Current Pipeline

```text
Candidate Profile + Job Description
-> Resume Analysis
-> Final Resume
-> Validation
-> Export Payload
-> DOCX Export
-> Streamlit Demo
```

## Project Structure

- `engine/` - deterministic analysis, validation, export, and orchestration modules
- `models/` - shared data models such as job descriptions and evidence
- `data/reference/` - reference skills data used by deterministic categorization
- `tests/` - pytest coverage for pipeline modules and smoke tests
- `samples/` - sample candidate and job JSON for demos
- `app.py` - local Streamlit demo UI

## Setup

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

If you commonly use `py`:

```powershell
py -m pip install -r requirements.txt
```

## Run Tests

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Latest local result after Sprint 29: 311 passed.

## Run Streamlit Demo

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

or:

```powershell
.\venv\Scripts\streamlit.exe run app.py
```

Then:

- Open http://localhost:8501
- Use the sample Administrative Assistant profile
- Click Run Analysis
- Download the generated DOCX

## Sample Data

- `samples/sample_profile_admin.json`
- `samples/sample_job_admin.json`

## Current Limitations

- Gemini/real LLM integration is not active yet.
- Search Grounding is not used for candidate resume claims.
- Search Grounding may be added later only for market context, such as UAE job trends or salary insights.
- DOCX styling is basic.
- Streamlit UI is a local demo, not a production app.
- Reference skills data is still limited and may be expanded later.

## Roadmap

- Demo polish
- Better DOCX styling
- More sample profiles
- Expanded reference skills
- Optional Gemini professional summary integration after safety controls
- Market context grounding for UAE trends, not candidate claims
