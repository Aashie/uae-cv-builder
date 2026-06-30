# Skill Gap Analyzer

## Objective

Analyze missing skills from the Matcher Engine and determine whether those gaps are critical or minor.

The goal is to explain why a candidate may not be a strong match and provide a foundation for future recommendations.

---

## Deliverable

Files:

- engine/skill_gap_analyzer.py
- tests/test_skill_gap_analyzer.py

---

## Inputs

Matcher Output

Example:

{
  "matched_skills": [],
  "missing_skills": [],
  "evidence_matches": {},
  "score": 0
}

---

## Outputs

{
  "critical_gaps": [],
  "minor_gaps": [],
  "application_readiness": ""
}

---

## V1 Rules

- All missing skills are considered critical.
- Minor gaps are not used in V1.
- Readiness levels:

  High:
  - Score >= 80

  Medium:
  - Score >= 50 and < 80

  Low:
  - Score < 50

- Critical gaps come directly from missing skills.

---

## Success Criteria

- Correct readiness calculation.
- Correct critical gap extraction.
- Handles empty inputs safely.
- Returns predictable output structure.

---

## Tests

- High readiness
- Medium readiness
- Low readiness
- Empty matcher output
- Missing skills become critical gaps
- Empty missing skills list

---

## Commit

git commit -m "Add Skill Gap Analyzer"