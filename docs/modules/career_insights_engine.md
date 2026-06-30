# Career Insights Engine

## Objective

Analyze extracted evidence to identify the candidate's strongest demonstrated skills.

This module focuses on understanding the candidate profile itself, independent of any specific job description.

---

## Deliverable

Files:

- engine/career_insights_engine.py
- tests/test_career_insights_engine.py

---

## Inputs

Evidence objects

Each Evidence object may contain:

- id
- source_type
- source_id
- category
- text
- skills
- confidence

---

## Outputs

{
  "strongest_skills": [],
  "skill_frequency": {},
  "total_evidence_items": 0,
  "total_unique_skills": 0
}

---

## V1 Rules

- Count skill frequency across Evidence objects.
- Skills are matched case-insensitively.
- Preserve clean title-style skill names in output.
- strongest_skills are sorted by frequency descending.
- If frequencies are tied, sort alphabetically.
- Empty evidence returns empty results.
- No AI.
- No career path prediction in V1.
- No weak skill calculation in V1.

---

## Success Criteria

- Correctly counts skills across evidence.
- Handles duplicate casing.
- Sorts strongest skills predictably.
- Handles empty evidence safely.
- Returns deterministic output.

---

## Tests

- Empty evidence
- Single evidence item
- Multiple evidence items
- Case-insensitive skill counting
- Strongest skills sorted by frequency
- Tied skills sorted alphabetically
- Total evidence item count
- Total unique skill count

---

## Commit

git commit -m "Add Career Insights Engine"