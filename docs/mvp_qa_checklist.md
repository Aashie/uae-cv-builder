# MVP QA Checklist

## Purpose

This checklist verifies the real Upload CV + Paste JD flow and Advanced Demo Mode for the current MVP. It is meant to catch safety, usability, and regression issues before future sprint work is committed.

## Preconditions

- Python virtual environment activated
- Dependencies installed
- Working tree clean
- Tests passing
- Streamlit app starts

## Automated Test Check

Command:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Expected:

- Full suite passes
- Latest Sprint 51 result: `449 passed`

## Real Upload Flow QA

### 1. App Startup

- Run `streamlit run app.py`.
- Confirm the app loads.
- Confirm title and subtitle appear.

### 2. CV Upload

- Upload a PDF or DOCX CV.
- Confirm file name, file type, and file size show.
- Confirm text extraction succeeds.
- Confirm character count appears.
- Confirm extracted text preview appears.

### 3. Candidate Parsing

- Confirm Candidate Profile Preview appears.
- Confirm candidate name appears when available.
- Confirm skill count appears.
- Confirm experience count appears.
- Confirm certification count appears when available.
- Confirm parser warnings/errors, if any, show line-by-line.

### 4. JD Paste And Parsing

- Paste a full job description.
- Confirm Job Description Preview appears.
- Confirm required skills and requirements/keywords counts appear.
- Confirm warnings/errors show line-by-line.
- Confirm missing job title warnings do not block analysis by themselves unless parser status fails.

### 5. Candidate Review

- Confirm Review Parsed Candidate Profile appears.
- Edit only true/supported information.
- Save reviewed profile.
- Confirm reviewed profile saved message appears.
- Confirm message says analysis becomes available after valid JD parse.

### 6. Analyze Button Readiness

- Confirm Analyze My CV is disabled when required inputs are missing.
- Confirm readiness checklist explains missing items.
- Confirm Analyze My CV becomes available only after:
  - CV extracted
  - Reviewed profile saved
  - JD pasted
  - JD parsed successfully

### 7. Analysis Results

- Run Analyze My CV.
- Confirm Analysis Results appears.
- Confirm warnings/errors show line-by-line.
- Confirm internal status appears.
- Confirm matched skills/missing skills/gap summary/recommendations appear where available.

### 8. Evidence Trace

- Confirm Evidence Trace section appears.
- Confirm it says section-level evidence trace, not per-claim proof.
- If analysis is successful, confirm section traces appear.
- If analysis is partial/failed, confirm trace is safely withheld with an explanation.

### 9. Download Safety Check

- Confirm Download Safety Check appears.
- Confirm DOCX download is blocked when:
  - Analysis is partial/failed
  - Validation fails
  - Evidence trace is missing/failed where required
  - Analysis is stale after CV/JD/profile changes
- Confirm blockers show line-by-line.
- Confirm DOCX download appears only when all safety checks pass.

### 10. Stale Analysis Check

- Run analysis.
- Change pasted JD text.
- Confirm previous DOCX download becomes blocked.
- Confirm user must rerun analysis.

### 11. No-Invention Check

- Paste a JD containing skills not present in the candidate profile.
- Confirm JD-only skills appear as gaps/recommendations.
- Confirm JD-only skills are not inserted into reviewed candidate profile.

## Advanced Demo Mode QA

1. Expand Advanced Demo Mode.
2. Confirm sample candidate JSON appears.
3. Confirm structured JD fields appear.
4. Run/observe demo analysis.
5. Confirm Results Dashboard appears.
6. Confirm Resume Preview appears.
7. Confirm DOCX Export section appears.
8. Confirm demo DOCX download button renders when validation passes.
9. Confirm Advanced Demo Mode remains separate from the real upload flow.

## Regression Safety Checklist

Before committing any future sprint:

- Run focused tests for the changed area.
- Run full test suite.
- Confirm no forbidden files changed.
- Confirm no-invention boundary remains intact.
- Confirm download gate is not weakened.
- Confirm stale-analysis blocking still works.
- Confirm warnings/errors are user-readable.
- Confirm Advanced Demo Mode still works if `app.py` changes.

## Known MVP Limitations

- Parser quality depends on CV/JD text clarity.
- Some PDF layouts may extract imperfect text.
- Match score is not a guarantee of recruiter/ATS outcome.
- Evidence trace is section-level only.
- Generated resume still needs human review.
- The project is not yet a full career intelligence platform.
