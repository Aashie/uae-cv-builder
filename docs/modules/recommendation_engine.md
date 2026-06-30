# Recommendation Engine

## Objective

Convert match results, skill gaps, and score data into deterministic recommendations.

The Recommendation Engine must help users understand what to highlight and what to improve without inventing skills or experience.

---

## Deliverable

Files:

- engine/recommendation_engine.py
- tests/test_recommendation_engine.py

---

## Inputs

Matcher Output

- matched_skills
- missing_skills
- evidence_matches
- score

Skill Gap Output

- critical_gaps
- minor_gaps
- application_readiness

Score Output

- match_score
- matched_skill_count
- required_skill_count

---

## Outputs

{
  "readiness_tier": "",
  "resume_recommendations": [],
  "career_recommendations": []
}

---

## V1 Rules

- Resume recommendations come from matched_skills.
- Career recommendations come from critical_gaps.
- Do not recommend highlighting a missing skill.
- Do not recommend learning a skill already matched.
- No AI generation.
- No hallucinated skills.
- No certifications, education, or experience weighting in V1.

---

## Readiness Tier

90–100 = Ready to Apply

70–89 = Apply with Minor Gaps

40–69 = Targeted Upskilling Recommended

0–39 = Significant Upskilling Required

---

## Success Criteria

- Correct readiness tier.
- Resume recommendations use only matched skills.
- Career recommendations use only critical gaps.
- Handles empty inputs safely.
- Returns predictable structure.

---

## Tests

- Ready to Apply
- Apply with Minor Gaps
- Targeted Upskilling Recommended
- Significant Upskilling Required
- Matched skills become resume recommendations
- Critical gaps become career recommendations
- Empty inputs
- No overlap between resume and career recommendations

---

## Commit

git commit -m "Add Recommendation Engine"