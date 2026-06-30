# Resume Analysis Orchestrator

## Objective

Provide a single entry point for the complete resume analysis pipeline.

The orchestrator coordinates all completed engines and produces a unified output package.

It does not perform file loading, JSON loading, Streamlit handling, or direct API calls.

---

## Deliverable

Files:

- engine/resume_analysis_orchestrator.py
- tests/test_resume_analysis_orchestrator.py

---

## Inputs

```python
profile
job_description
```

The orchestrator receives clean objects only.

File loading is the caller's responsibility.

Example:

```python
profile = load_profile("data/profiles/sample_profile.json")
job_description = parse_job_description(raw_text)

result = run_resume_analysis(profile, job_description)
```

---

## Hard Stop Conditions

Immediately return:

```python
{
    "status": "failed",
    "errors": [...]
}
```

When:

- profile is None
- profile is empty
- job_description is None
- job_description.required_skills is missing or empty

No downstream modules execute.

Note:

job_title alone is not enough to continue. Required skills drive matching, scoring, gap analysis, and recommendations.

---

## Soft Failure Conditions

Pipeline continues.

Errors are collected.

Examples:

- recommendation engine failure
- career insights failure
- summary generator fallback

Result:

```python
status = "partial"
```

---

## Pipeline

```text
Evidence Extractor
↓
Career Insights Engine
↓
Matcher
↓
Scorer
↓
Skill Gap Analyzer
↓
Recommendation Engine
↓
Prompt Builder
↓
Resume Draft Builder
↓
Professional Summary Generator
↓
AI Response Validator
↓
Hallucination Checker
↓
Resume Output
```

---

## Safety Layer

The orchestrator must always run AI output through:

1. AI Response Validator
2. Hallucination Checker

before returning final resume output.

Validator performs structural checks.

Hallucination Checker performs evidence checks.

In V1, Hallucination Checker checks `experience_bullets` only.

Professional summary hallucination checking is deferred to V2.

---

## Output Schema

```python
{
    "status": "",
    "errors": [],

    "match_score": 0,
    "matched_skills": [],
    "missing_skills": [],

    "skill_gaps": {
        "critical_gaps": [],
        "minor_gaps": []
    },

    "recommendations": {
        "resume_recommendations": [],
        "career_recommendations": []
    },

    "readiness_tier": "",

    "career_insights": {},

    "resume_draft": {},

    "summary": "",

    "ai_validation": {
        "is_valid": false,
        "errors": []
    },

    "hallucination_check": {
        "passed_bullets": [],
        "failed_bullets": [],
        "hallucination_count": 0
    }
}
```

---

## Status Values

### success

All required modules complete successfully.

```python
status = "success"
errors = []
```

---

### partial

One or more soft failures occurred, but a usable result was still produced.

```python
status = "partial"
errors != []
```

---

### failed

A hard stop condition occurred.

```python
status = "failed"
```

No meaningful analysis is returned.

---

## Module Responsibilities

### Evidence Extractor

Converts profile data into Evidence objects.

### Career Insights Engine

Analyzes Evidence objects and identifies strongest demonstrated skills.

### Matcher

Compares job required skills against profile skills and evidence skills.

### Scorer

Calculates Match Score from matcher output.

### Skill Gap Analyzer

Classifies missing skills into gaps and readiness.

### Recommendation Engine

Creates resume and career recommendations.

### Prompt Builder

Aggregates intelligence outputs into a prompt package.

### Resume Draft Builder

Creates deterministic resume draft from prompt package.

### Professional Summary Generator

Generates or falls back to a professional summary.

### AI Response Validator

Checks AI output structure.

### Hallucination Checker

Checks AI-generated experience bullets against linked evidence.

---

## Success Criteria

- Single orchestration entry point
- No filesystem access
- No direct Streamlit dependency
- No direct JSON loading
- Hard stop behavior implemented
- Soft failure behavior implemented
- Safety layer included
- AI output validated before final output
- Hallucination check included before final output
- Deterministic output schema
- Errors collected consistently

---

## Tests

- Successful pipeline
- Empty profile hard stop
- Missing job description hard stop
- Missing required skills hard stop
- Recommendation engine soft failure
- Career insights soft failure
- Summary generator fallback
- AI validator failure creates partial status
- Hallucination checker failure creates partial status
- Safety layer output included
- Success status returned
- Partial status returned
- Failed status returned
- Output schema contains required top-level fields

---

## Commit

```bash
git commit -m "Add Resume Analysis Orchestrator"
```