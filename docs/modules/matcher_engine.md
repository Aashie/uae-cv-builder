# Matcher Engine

## Objective

Compare a parsed Job Description against the user's profile skills and extracted evidence.

The Matcher Engine helps determine how well a candidate fits a job based on real profile data, not AI guesses.

---

## Deliverable

Files:

- engine/matcher.py
- tests/test_matcher.py

---

## Inputs

- JobDescription object
- Profile skills
- Evidence objects

---

## Outputs

Dictionary containing:

- matched_skills
- missing_skills
- evidence_matches
- score

---

## Matching Rules

- Compare job required skills against profile skills.
- Compare job required skills against skills attached to Evidence objects.
- A skill is considered matched if it appears in either profile skills or evidence skills.
- A skill is missing if it appears in the job description but not in profile skills or evidence skills.
- Basic score is calculated as:

matched skills / required skills * 100

---

## Success Criteria

- Match skills from profile data.
- Match skills from Evidence objects.
- Identify missing skills.
- Calculate score correctly.
- Handle empty skills safely.
- Return predictable structured output.

---

## Tests

- Match using profile skills only
- Match using evidence skills only
- Match using both profile and evidence skills
- Identify missing skills
- Calculate basic score
- Handle empty required skills
- Handle empty profile and evidence

---

## Commit

git commit -m "Add Matcher Engine"

## Sprint Outcome

Implemented:
- Profile skill matching
- Evidence skill matching
- Missing skill detection
- Evidence-to-skill traceability
- Basic scoring

Validation:
- 8 matcher tests passing

Future Enhancements:
- Weighted scoring
- Certification matching
- Experience matching
- Semantic skill matching
- Industry matching