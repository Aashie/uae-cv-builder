# UAE CV Builder / ATS Career Intelligence MVP

This is an evidence-based resume analysis and DOCX generation MVP for UAE job applications. It allows a user to upload a CV, review extracted candidate evidence, paste a job description, compare the reviewed profile against the JD, view gaps and recommendations, and download a reviewed resume only when safety checks pass.

The project follows a strict no-invention rule. It may structure, categorize, validate, and export candidate-provided data, but it must not invent skills, achievements, job titles, credentials, education, tools, metrics, UAE experience, or work history.

## Current MVP Capabilities

- PDF/DOCX CV upload
- Text extraction preview
- Candidate profile parsing
- Human review/edit step
- JD paste and parsing
- Real upload-based analysis using `reviewed_candidate_profile`
- Skill matching and gap summary
- Recommendations
- Section-level evidence trace
- Stale-analysis detection
- Safe DOCX download gate
- Advanced Demo Mode for structured sample testing
- Regression tests for Admin Assistant, Customer Service, and IT Support fixtures

## What The MVP Intentionally Does Not Do

- Does not invent missing skills or experience
- Does not silently add JD-only skills to the candidate profile
- Does not guarantee perfect ATS scoring
- Does not provide per-claim evidence proof yet
- Does not guarantee every generated sentence is final human-ready
- Does not bypass validation to create DOCX
- Does not treat parser output as final evidence without user review

## Safety Model

```text
uploaded CV text
-> parsed_candidate_profile
-> user-reviewed reviewed_candidate_profile
-> JD parsing
-> analysis
-> validation
-> evidence trace
-> DOCX gate
```

After review, `reviewed_candidate_profile` is the canonical candidate evidence for the real upload flow. `parsed_candidate_profile` is raw parser output and must not be treated as final after the user review step.

JD skills can influence matching, gaps, and recommendations. They must never be inserted into candidate evidence. Missing JD skills must remain gaps or recommendations only.

Final resume output must pass validation before DOCX download. Download must remain blocked if validation fails, analysis is stale, or the required section-level evidence trace is missing or failed. The evidence trace is section-level only, not per-claim proof.

## Project Structure

- `engine/` - deterministic analysis, parsing, validation, export, and orchestration modules
- `models/` - shared data models such as job descriptions and evidence
- `data/reference/` - reference skills data used by deterministic categorization
- `tests/` - pytest coverage for pipeline modules, smoke tests, and real-flow fixtures
- `samples/` - sample candidate and job JSON for demos
- `app.py` - local Streamlit demo UI
- `docs/mvp_qa_checklist.md` - manual QA checklist for the current MVP

## Installation / Setup

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

If you commonly use `py`:

```powershell
py -m pip install -r requirements.txt
```

## Run Streamlit

```powershell
streamlit run app.py
```

Alternative:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

Then open http://localhost:8501.

## Running Tests

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Latest local result after Sprint 51 documentation update: `449 passed`.

## Main User Workflow

1. Upload PDF/DOCX CV.
2. Review extracted CV text.
3. Review parsed candidate profile.
4. Edit only true/supported information.
5. Save reviewed profile.
6. Paste full JD.
7. Preview parsed JD.
8. Run Analyze My CV.
9. Review matches, gaps, and recommendations.
10. Review Evidence Trace and Download Safety Check.
11. Download DOCX only if the safety gate passes.

## Manual QA Checklist

Use [docs/mvp_qa_checklist.md](docs/mvp_qa_checklist.md) before committing or releasing changes that affect the real upload flow, Streamlit UI, parsing, analysis, evidence trace, validation, or DOCX download.

## Sample Data

- `samples/sample_profile_admin.json`
- `samples/sample_job_admin.json`

## Development Notes

- Keep changes small and sprint-based.
- Prefer deterministic logic before AI behavior.
- Add regression tests before risky refactors.
- Do not weaken no-invention boundaries.
- Do not loosen stale-analysis, validation, or evidence-trace download gates.
- Keep Advanced Demo Mode separate from the real upload flow unless a sprint explicitly says otherwise.

## Known MVP Limitations

- Parser quality depends on CV/JD text clarity.
- Some PDF layouts may extract imperfect text.
- Match score is not a guarantee of recruiter or ATS outcome.
- Evidence trace is section-level only.
- Generated resume still needs human review.
- Streamlit UI is a local MVP, not a production app.
- Reference skills data is still limited and may be expanded later.
- Gemini/real LLM integration is not active for candidate claim generation.
- Search Grounding is not used for candidate resume claims.
