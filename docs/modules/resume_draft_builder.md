# Resume Draft Builder

## Objective

Convert a prompt package into a structured resume draft.

This is the final deterministic layer before AI-generated resume content.

---

## Deliverable

Files:

- engine/resume_draft_builder.py
- tests/test_resume_draft_builder.py

---

## Inputs

Prompt Package

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

## Outputs

{
  "job_title": "",
  "professional_summary": "",
  "key_skills": [],
  "matched_skills": [],
  "resume_bullets": []
}

---

## V1 Rules

- No AI.
- No PDF generation.
- No markdown generation.
- professional_summary must be deterministic.
- key_skills come from strongest_skills.
- matched_skills copied directly.
- resume_bullets come from resume_recommendations.

---

## Success Criteria

- Correct field mapping.
- Handles missing inputs.
- Handles empty inputs.
- Produces deterministic output.

---

## Tests

- Complete input
- Empty input
- Missing keys
- Summary generation
- Key skills mapping
- Matched skills mapping
- Resume bullet mapping

---

## Commit

git commit -m "Add Resume Draft Builder"