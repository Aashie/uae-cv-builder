# Prompt Builder

## Objective

Aggregate outputs from the intelligence layer into a structured prompt package.

This module prepares clean, validated context for future AI resume generation.

---

## Deliverable

Files:

- engine/prompt_builder.py
- tests/test_prompt_builder.py

---

## Inputs

Job Description

Matcher Output

Score Output

Skill Gap Output

Recommendation Output

Career Insights Output

---

## Outputs

{
  "job_title": "",
  "match_score": 0,
  "strongest_skills": [],
  "matched_skills": [],
  "critical_gaps": [],
  "resume_recommendations": [],
  "career_recommendations": []
}

---

## V1 Rules

- No AI calls.
- No prompt text generation.
- Only aggregate validated outputs.
- Missing inputs should be handled safely.
- Return deterministic structure.

---

## Success Criteria

- Correct aggregation.
- Handles missing fields.
- Handles empty inputs.
- Produces consistent structure.

---

## Tests

- Complete inputs
- Empty inputs
- Missing keys
- Correct field mapping
- Job title extraction
- Match score mapping

---

## Commit

git commit -m "Add Prompt Builder"