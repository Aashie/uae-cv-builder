# Project State

## 1. Project Identity

- Project name: ATS-UAE-RESUME-BUILDER / UAE CV Builder
- Repository path: `C:\Users\hp\Desktop\uae-cv-builder`
- Tech stack: Python, Streamlit, pytest, python-docx, pypdf
- Product type: evidence-based resume analysis and DOCX generation for UAE job applications

## 2. Core No-Invention Rule

- No invented candidate claims: skills, tools, certifications, degrees, companies, job titles, dates, years of experience, achievements, UAE experience, language ability, salary, or responsibilities.
- JD-only requirements stay as gaps, recommendations, "add this only if true" guidance, or future roadmap items.
- Resume claims must trace to candidate evidence or reviewed profile text.
- If uncertain, preserve or block; never invent.

## 3. Workflow Rules & Roles

- ChatGPT plans and architects sprint scope.
- Gemini/Kimi reviews plans, risks, and proposed changes.
- Codex/Cursor implements narrowly inside allowed files only.
- User manually verifies real app behavior and edge cases.
- ChatGPT approves commit readiness.
- User commits and pushes.
- Codex must not commit, push, or tag unless explicitly instructed.

## 4. Latest Known State

- Latest known commit: `8741469 Sprint 63: split candidate skill bullet blocks`
- Latest known full suite: `474 passed`
- Working tree expected clean after Sprint 63.

## 5. Standard Commands

Status:

```powershell
git status --short
```

Log:

```powershell
git log --oneline -5
```

Full tests:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Candidate parser tests:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_candidate_profile_text_parser.py -q
```

JD parser tests:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_job_description_text_parser.py -q
```

Matcher tests:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_matcher.py -q
```

Final resume validator tests:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_final_resume_schema_validator.py -q
```

Streamlit:

```powershell
.\venv\Scripts\streamlit.exe run app.py
```

## 6. Current Real-Flow Pipeline Map

CV upload -> text extraction -> candidate parser -> reviewed candidate profile -> JD parser -> matcher -> scorer -> skill gap analyzer -> recommendation engine -> prompt builder -> resume draft builder -> skills section generator -> professional summary generator -> experience bullet generator -> hallucination checker -> resume output assembler -> final resume schema validator -> evidence trace -> DOCX download gate

## 7. Completed Sprint Log

- Sprint 53: clarified Developer Sample Mode.
- Sprint 55B: fixed real-flow Analyze gate state persistence.
- Sprint 56: contained Developer Sample Mode results and disabled sample DOCX export.
- Sprint 58: classified JD non-skill requirements into education/experience.
- Sprint 59: added conservative matcher normalization for MS Office and CRM.
- Sprint 62: enforced final resume usefulness validation.
- Sprint 63: split candidate skill bullet blocks.

## 8. Current Known Backlog

- Job title parser still misses Sales Executive heading variants.
- Candidate parser still needs language extraction.
- Candidate parser still needs certification block cleanup for some CVs.
- Experience role segmentation still merges some roles/bullets.
- Recommendations are still awkward for full JD phrases.
- UI tag display glues badges/text together in some outputs.
- Resume generation quality still weak after validation blocks unsafe download.
- Need better evidence trace granularity later.
- Need Master Profile + Evidence Ledger architecture later.

## 9. Safety Gates

- Reviewed candidate profile must be saved before real analysis.
- JD must parse successfully.
- Final resume validation must pass.
- Evidence trace must exist.
- DOCX download must remain blocked when validation, evidence, or stale checks fail.
- Weak/empty resume output must not be download-ready.

## 10. Codex Must Never Do

- Never edit outside allowed files.
- Never broaden scope.
- Never invent candidate facts.
- Never add JD-only skills to candidate profile.
- Never change generators, parsers, or matcher unless the sprint allows it.
- Never commit, push, or tag unless explicitly instructed.
- Never silently ignore failing tests.
- Never treat sample mode as real flow.
