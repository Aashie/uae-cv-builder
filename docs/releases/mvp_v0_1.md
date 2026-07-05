# MVP v0.1 Release Notes

## Status

This is a local MVP baseline for the UAE CV Builder / ATS Career Intelligence project. It is ready for controlled local testing, not production deployment.

## Verification Summary

- Full pytest command used: `.\venv\Scripts\python.exe -m pytest -q`
- Pytest result from this sprint: `449 passed in 5.31s`
- Streamlit startup smoke result: `streamlit_status=200`
- Git working tree status before release-note changes: clean
- Git working tree status after creating release note, before staging: `docs/releases/` untracked

## What This MVP Can Do

- Upload PDF/DOCX CV
- Extract CV text
- Parse candidate profile from extracted text
- Let user review/edit parsed candidate profile
- Use `reviewed_candidate_profile` as canonical real-flow evidence
- Paste and parse a job description
- Run real upload-based analysis
- Show matched skills, missing skills, gaps, and recommendations
- Show section-level evidence trace when analysis is successful enough
- Block evidence trace when analysis is partial/failed
- Detect stale analysis after CV/JD/profile changes
- Gate real-flow DOCX download behind validation, freshness, and evidence trace checks
- Keep Advanced Demo Mode separate for structured sample testing
- Export DOCX in demo/valid gated flows

## What This MVP Intentionally Does Not Do

- Does not invent missing candidate skills or experience
- Does not add JD-only skills into candidate profile
- Does not guarantee recruiter or ATS outcomes
- Does not provide per-claim evidence proof yet
- Does not make every generated sentence final without human review
- Does not bypass safety validation for DOCX export
- Does not act as a full career intelligence platform yet

## Safety Baseline

```text
uploaded CV text
-> parsed_candidate_profile
-> reviewed_candidate_profile
-> JD parsing
-> analysis
-> validation
-> evidence trace
-> DOCX gate
```

`reviewed_candidate_profile` is canonical after review. `parsed_candidate_profile` is raw parser output and must not be treated as final candidate evidence after the review step.

JD data can influence matching, gaps, and recommendations only. Candidate evidence must come from the CV or user-reviewed edits. JD-only skills must remain gaps/recommendations and must never add skills, experience, or certifications to candidate evidence.

Download gating is intentionally strict. DOCX download remains blocked if validation fails, analysis is stale, or the required section-level evidence trace is missing or failed. The evidence trace is section-level only, not per-claim proof.

## Test Coverage Baseline

Current automated baseline: `449 passed`.

Coverage includes:

- Parser tests
- Upload/paste analysis pipeline tests
- Evidence trace tests
- DOCX/export validation tests
- Real-flow E2E fixtures for:
  - Administrative Assistant
  - Customer Service Representative
  - IT Support Assistant

## Manual QA Baseline

Manual QA should follow `docs/mvp_qa_checklist.md`.

Manual QA should cover:

- Real upload flow
- JD parsing warnings/errors
- Reviewed profile save
- Analyze My CV readiness
- Evidence trace behavior
- Download Safety Check
- Stale-analysis blocking
- No-invention behavior
- Advanced Demo Mode separation

## Known Limitations

- PDF extraction depends on document layout
- Parser quality depends on text clarity
- Match score is directional, not a guarantee
- Evidence trace is section-level only
- Real-flow resume output still requires human review
- Streamlit app is local MVP UI, not production
- AI/Gemini generation is not active for candidate claim creation

## Suggested Tag

Suggested Git tag after review:
`mvp-v0.1`

Suggested commands, not run during this sprint:

```powershell
git tag -a mvp-v0.1 -m "MVP v0.1 safe baseline"
git push origin mvp-v0.1
```

## Next Recommended Work After v0.1

- Improve final resume content quality while preserving evidence safety
- Add stronger role-specific fixtures
- Add per-claim evidence trace later
- Improve DOCX styling
- Expand reference skills data
- Prepare broader career intelligence modules after the MVP baseline
