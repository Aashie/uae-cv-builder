# Scoring Engine

## Objective

Calculate a transparent Match Score between a Job Description and a candidate profile.

The score must be deterministic, explainable, and easy to validate.

---

## Deliverable

Files:

- engine/scorer.py
- tests/test_scorer.py

---

## Inputs

Matcher Output

Example:

{
  "matched_skills": [],
  "missing_skills": [],
  "evidence_matches": {}
}

JobDescription

---

## Outputs

{
  "match_score": 0,
  "matched_skill_count": 0,
  "required_skill_count": 0
}

---

## Formula

Match Score =
matched required skills /
total required skills × 100

---

## Rules

- All skills have equal value.
- Only skills affect the score.
- Evidence weighting is not included.
- Certifications are not included.
- Education is not included.
- Experience is not included.

---

## Success Criteria

- Correct score calculation
- Handle zero required skills
- Return structured output
- Deterministic results

---

## Tests

- Perfect match
- Partial match
- No match
- Empty required skills
- Empty matcher output

---

## Commit

git commit -m "Add Scoring Engine"