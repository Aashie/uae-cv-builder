# Product Requirements Document
## UAE Career Intelligence Platform

**Repository:** `uae-cv-builder`  
**Version:** 2.1  
**Author:** Aashutosh Badal  
**Status:** Active — repository-aligned  
**Date:** July 2026  
**Verified test state:** 505 passing tests, with one pytest cache-write warning  
**Latest sprint represented:** Sprint 66G

---

## 1. Executive Summary

The UAE Career Intelligence Platform is an evidence-based career guidance product for professionals navigating the UAE job market. It compares user-confirmed career evidence with a specific job description, explains supported matches and genuine gaps, and produces an ATS-friendly structured DOCX only when the current validation and evidence gates pass.

The product is not a generic AI resume generator. Its governing rule is **NO INVENTION**: job-description requirements must not be converted into candidate claims unless the reviewed candidate profile contains supporting evidence.

The current product is a local Streamlit MVP with a working real-user flow:

```text
Upload CV
→ extract text
→ parse candidate profile
→ review and save profile
→ paste and parse JD
→ analyze match and gaps
→ generate resume components
→ build section-level evidence trace
→ apply DOCX safety gate
→ download DOCX when allowed
```

The current controls are layered and deterministic, but they are not comprehensive per-claim verification. Final-resume skills receive direct support checks. Generated experience bullets have partial evidence-ID and keyword-overlap validation. Professional-summary and experience coverage remains section-level.

There is no production deployment, authentication, user database, persistent per-user Master Profile, persistent Evidence Ledger, or live Gemini generation in the real flow.

The next major architecture milestone is an integrated Master Profile and persistent Evidence Ledger.

---

## 2. Product Vision

**One-sentence vision**

Know your true fit for any role, generate a proof-backed CV when ready, and receive a structured path when you are not.

The product is intended to grow from a safe resume-analysis MVP into a UAE-focused career intelligence platform. Its long-term value comes from connecting career evidence, job requirements, resume generation, skill-gap prioritization, and practical next steps without fabricating candidate credentials.

### What the product is

- An evidence-based career intelligence platform
- A job-specific CV analysis and generation workflow
- A transparent comparison between reviewed candidate evidence and JD requirements
- A foundation for future career planning, evidence tracking, and UAE market intelligence

### What the product is not

- A generic AI CV generator
- A job board or recruitment marketplace
- A replacement for employer ATS systems
- A system that guarantees ATS acceptance, interviews, or employment
- A system that invents qualifications to improve a match score

---

## 3. Problem Statement

### Problem 1 — Every application needs different emphasis

Candidates often reuse one generic CV across many roles. Relevant experience, terminology, and skills may not be presented in the way a specific vacancy requires. Candidates need job-specific guidance without converting JD language into unsupported personal claims.

### Problem 2 — Candidates do not know what is actually missing

A fit score alone is insufficient. Candidates need to understand which requirements are supported, which are missing, and what evidence caused a match. Current evidence mapping is partial, but the product direction is explicit: every match should become increasingly explainable.

### Problem 3 — Generative tools can invent candidate facts

Resume tools may add achievements, metrics, skills, tools, responsibilities, or experience that the candidate never supplied. This creates ethical and practical risks, including interview inconsistency and background-check exposure.

### Problem 4 — Low-fit candidates need a path forward

When a candidate is not ready for a target role, the useful outcome is not fabricated resume content. The product should preserve the gap and ultimately provide an ordered, evidence-aware learning and career roadmap.

### UAE-specific context

The UAE market includes regional credentials, visa and mobility considerations, role-specific Arabic requirements, and sector-specific expectations such as RERA, AML, DHA, and KHDA. Generic career tools do not consistently represent this context. UAE market intelligence is part of the product vision, but it is not built in the current MVP.

---

## 4. Target Users

### Primary — Career Switcher

**Situation:** Employed, underemployed, or recently unemployed and targeting a different role or industry.  
**Need:** Honest job-fit analysis, evidence-backed CV emphasis, and clarity about missing requirements.

### Secondary — Upskiller

**Situation:** Has a target role but is not yet fully qualified.  
**Need:** Prioritized skill gaps and, in future phases, an actionable UAE-relevant learning roadmap and progress tracker.

### Tertiary — Fresh Graduate

**Situation:** Has limited work experience but may have relevant education, projects, internships, languages, or certifications.  
**Need:** An honest presentation of existing evidence without invented experience or inflated seniority.

---

## 5. Current MVP Scope

The current MVP supports one main local use case: upload a CV, review the parser output, compare the reviewed profile with a pasted JD, inspect the results, and download a DOCX when all current gates pass.

| Capability | Current status | Accuracy note |
|---|---|---|
| PDF and DOCX CV upload | Built | Scanned-image PDF OCR is not built |
| Text extraction | Built | Supports selectable PDFs and DOCX |
| Candidate text parser | Built | Deterministic and intentionally narrow |
| Candidate review/edit/save UI | Built | Stored in Streamlit session state only |
| Reviewed profile in the real flow | Built | Required before real-flow analysis |
| JD text parser | Built | Heading-dependent and imperfect |
| Matcher and score calculation | Built | Deterministic, conservative matching |
| Skill-gap analyzer | Built | All unmatched required skills are currently critical |
| Recommendation engine | Built | Deterministic; wording remains mechanical |
| Resume draft builder | Built | Intermediate deterministic structure |
| Skills-section generator | Built | Direct skill-safety controls apply |
| Professional-summary generator | Built | Not comprehensively claim-traced |
| Experience-bullet generator | Built | Includes evidence IDs; validation is partial |
| Experience-bullet hallucination checker | Built | ID and keyword-overlap checks; not universal |
| Resume output assembler | Built | Implemented in `resume_output_assembler.py` |
| Final-resume schema validator | Built | Validates structure and minimum usefulness |
| Section-level evidence trace | Built | Direct for skills; coarse for summary/experience |
| DOCX export adapter and exporter | Built | Produces an ATS-friendly structured DOCX |
| Real-flow DOCX safety gate | Built | Blocks stale, failed, invalid, or unsupported output |
| Stale-analysis detection | Built | Detects same-session input changes |
| Developer Sample Mode | Built | Separated from the real-user evidence flow |
| Automated test suite | Built | 505 tests currently pass |
| Comprehensive per-claim trace | Not built | Partial bullet evidence linkage exists |
| Persistent Master Profile | Not built | Preliminary static artifacts exist |
| Persistent Evidence Ledger | Not built | In-memory Evidence objects exist |
| Live Gemini real-flow generation | Not built | Current real flow is deterministic |

---

## 6. Current Application Status

**Application:** Local Streamlit MVP  
**Production deployment:** Not built  
**Authentication:** Not built  
**User database:** Not built  
**Persistent user profiles:** Not built  
**Persistent Master Profile:** Not built  
**Persistent Evidence Ledger:** Not built  
**Comprehensive per-claim trace:** Not built  
**Live Gemini real-flow generation:** Not built  
**Verified automated tests:** 505 passing, one pytest cache-write warning

### What a local user can do now

1. Upload a PDF or DOCX CV.
2. Extract text from the uploaded file.
3. Parse the text into the current candidate-profile shape.
4. Review, edit, and save the profile in the active Streamlit session.
5. Paste a raw-text job description.
6. Parse the JD.
7. Run deterministic matching, scoring, gap analysis, recommendations, and resume generation.
8. View matched skills, missing skills, recommendations, and a section-level evidence trace.
9. Download a DOCX when the safety gate passes.

### Recent verified behavior represented by Sprint 65B–66G

- Explicit language evidence can be routed into candidate skills.
- Narrow experience-derived skill extraction populates nested experience skills.
- Negation guards prevent selected false-positive extraction.
- Saving reviewed experience text recomputes nested experience skills.
- Microsoft Office and MS Office are conservatively aligned.
- Excel alone does not establish Microsoft Office or CRM.
- The trace checks top-level and nested experience skills.
- Unsupported final-resume skills block DOCX download.
- Missing JD job title support alone does not block download.

---

## 7. Core Safety Principles

These principles define the product boundary. Some are fully represented by current deterministic controls; others remain target requirements.

### Principle 1 — No invention

The system must not invent:

```text
skills
tools
certifications
degrees
job titles
companies
employment dates
years of experience
achievements
UAE experience
language ability
salary history
responsibilities
metrics
percentages
KPIs
```

### Principle 2 — Closed candidate-evidence boundary

JD-only requirements must not be promoted into candidate skills or resume claims. In the current implementation, unmatched required skills remain gaps and may feed deterministic recommendations.

“Add only if true” and future learning-roadmap treatments are product rules. They are not separate structured categories in the current gap engine.

### Principle 3 — Reviewed profile is canonical for the real user flow

```text
parsed_candidate_profile
= raw parser result
= unreviewed

reviewed_candidate_profile
= user-reviewed session-state profile
= canonical candidate input for the real upload/paste analysis flow
```

Real-flow analysis is blocked until a non-empty reviewed profile has been saved. Legacy and Developer Sample Mode paths are separate and must not be described as the canonical real-user flow.

User edits are treated as user-confirmed evidence. The UI instructs the user to add only information that is true and supported by the CV or the user's own knowledge. The product does not independently verify the truth of manually entered information.

### Principle 4 — Layered validation before download

The current product has layered deterministic no-invention controls:

- final-resume schema and usefulness validation;
- direct final-resume skill support checks;
- partial experience-bullet evidence-ID and keyword-overlap checking;
- section-level summary and experience trace;
- stale-input detection;
- real-flow pipeline status checks;
- DOCX gating.

These controls reduce unsupported output but do not constitute comprehensive semantic verification of every resume claim.

### Principle 5 — Search-grounding boundary

Future web or market data may inform market-context outputs such as UAE trends, salary information, or industry demand. It must not be used as candidate evidence or to create candidate qualifications.

---

## 8. Current User Journey

```text
1. Upload PDF or DOCX CV
   ↓
2. Extract document text
   ↓
3. Parse current candidate profile
   ↓
4. Review, edit, and save profile
   → reviewed_candidate_profile becomes the real-flow candidate input
   ↓
5. Paste raw JD text
   ↓
6. Parse JD
   → title, required skills, soft skills, experience, education,
     certifications, and keywords where explicitly extractable
   ↓
7. Run analysis pipeline
   → extract evidence records
   → match required skills
   → calculate score
   → classify current V1 gaps
   → generate recommendations
   → build prompts and deterministic resume draft
   → generate summary, skills, and experience bullets
   → validate experience bullets
   → assemble final resume
   → validate final-resume schema
   ↓
8. Build section-level evidence trace
   → direct final-skill support checking
   → section-level summary and experience support
   ↓
9. Display analysis and evidence information
   ↓
10. Apply real-flow DOCX gate
   → current-input/freshness checks
   → pipeline and analysis status checks
   → schema checks
   → evidence-trace checks
   → unsupported-skill checks
   ↓
11. Build export payload and DOCX
   ↓
12. Show download only when allowed
```

---

## 9. Current Technical Architecture

### UI and session workflow

```text
app.py
```

`app.py` contains the Streamlit UI, session-state workflow, review/save behavior, real-flow readiness checks, stale-analysis logic, evidence-trace display, and DOCX gate orchestration.

### Upload and extraction

```text
engine/resume_text_extractor.py
```

### Parsing

```text
engine/candidate_profile_text_parser.py
engine/job_description_text_parser.py
```

### Analysis and evidence

```text
engine/upload_paste_analysis_pipeline.py
engine/evidence_extractor.py
engine/matcher.py
engine/scorer.py
engine/skill_gap_analyzer.py
engine/recommendation_engine.py
engine/resume_analysis_orchestrator.py
```

### Drafting and generation

```text
engine/prompt_builder.py
engine/resume_draft_builder.py
engine/skills_section_generator.py
engine/professional_summary_generator.py
engine/experience_bullet_generator.py
```

### Validation and evidence controls

```text
engine/ai_response_validator.py
engine/hallucination_checker.py
engine/final_resume_schema_validator.py
engine/section_evidence_trace.py
```

### Assembly and export

```text
engine/resume_output_assembler.py
engine/resume_export_adapter.py
engine/docx_exporter.py
```

### Models

```text
models/job_description.py
models/evidence.py
```

### Current reference data

```text
data/reference/skills.json
data/reference/soft_skills.json
data/reference/education.json
data/reference/experience_levels.json
data/reference/certifications.json

utils/reference_loader.py
```

### Preliminary future-model artifacts

```text
data/master_profile.json
data/master_profile_schema.json
```

These files do not represent an integrated or persistent per-user Master Profile.

---

## 10. Current Actual Data Model

This section documents the repository's current data structures, not the desired future product schema.

### Current parsed and reviewed candidate profile

```json
{
  "name": "",
  "skills": [],
  "experience": [
    {
      "id": "exp-1",
      "text": "",
      "skills": []
    }
  ],
  "projects": [],
  "certifications": [],
  "achievements": []
}
```

The reviewed profile preserves these six top-level keys. It does not currently save email, phone, location, structured company, role, employment dates, responsibilities, or education as canonical top-level fields.

The parser may return contact, education-section text, language-section text, and other parsing information in result metadata. That metadata is not equivalent to the current saved canonical reviewed-profile schema.

### Current parser wrapper

Candidate and JD parsers return a wrapper broadly shaped as:

```json
{
  "status": "success",
  "errors": [],
  "warnings": [],
  "metadata": {},
  "candidate_profile": {}
}
```

The JD parser uses `job_description` instead of `candidate_profile`.

### Current JD model

```json
{
  "job_title": "",
  "required_skills": [],
  "soft_skills": [],
  "experience_level": "",
  "education": "",
  "certifications": [],
  "keywords": []
}
```

The parser can recognize a preferred-skills section in metadata, but the current `JobDescription` model and gap logic do not provide must-have versus preferred/nice-to-have classification.

### Current final-resume schema

```json
{
  "job_title": "",
  "professional_summary": "",
  "skills": {
    "technical": [],
    "soft": [],
    "tools": [],
    "domain": [],
    "matched_skills": [],
    "strongest_skills": []
  },
  "experience_bullets": [
    {
      "text": "",
      "source_evidence_id": ""
    }
  ],
  "metadata": {
    "assembled_by": "resume_output_assembler",
    "version": "v1",
    "summary_source": "",
    "bullet_source": "",
    "skills_source": ""
  }
}
```

The final-resume validator checks required sections, all six skill categories, minimum visible content, and selected weak-placeholder conditions. Schema validity does not prove that every claim is true.

---

## 11. Future Target Data Model

The future model should preserve structured career history and evidence across sessions and applications. It is not the current runtime schema.

### Target persistent Master Profile

A future `MasterProfile` should support, at minimum:

```json
{
  "personal_info": {
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "nationality": "",
    "visa_status": "",
    "uae_driving_license": null
  },
  "career_identity": {
    "current_title": "",
    "target_roles": []
  },
  "skills": [],
  "experience": [
    {
      "id": "",
      "company": "",
      "role": "",
      "start_date": "",
      "end_date": "",
      "responsibilities": [],
      "achievements": [],
      "skills": [],
      "evidence_ids": []
    }
  ],
  "education": [],
  "projects": [],
  "certifications": [],
  "languages": [],
  "preferences": {}
}
```

The exact schema requires a dedicated design and migration decision. This example is a target concept, not a claim about current storage.

### Target Evidence Ledger

A future persistent Evidence Ledger should:

- store evidence independently from any single CV;
- link each claim and skill to one or more source records;
- retain source type, source identity, text, dates, and review status;
- support user correction and removal;
- support durable confidence and provenance;
- expose why a skill or claim exists;
- support claim-level validation across summaries, bullets, skills, education, and credentials;
- prevent deleted or superseded evidence from silently remaining in generated CVs.

---

## 12. Current Evidence Model

### Implemented in-memory Evidence model

The repository contains a tested `Evidence` dataclass with:

```text
id
source_type
source_id
category
text
skills
confidence
```

The current evidence extractor creates in-memory records from:

- experience;
- projects;
- certifications;
- achievements.

IDs use category prefixes such as `EXP`, `PRJ`, `CERT`, and `ACH`.

This is a real current implementation, but it is not a persistent Evidence Ledger.

### Current skill evidence routes

Candidate skills can currently reach matching and trace behavior through:

1. Explicit top-level reviewed skills.
2. Explicit language evidence routed into reviewed skills.
3. Narrow experience-derived skills stored in `experience[i]["skills"]`.

The experience-derived route uses a closed extraction approach and selected negation guards. It must not be described as general skill inference.

### Current section-level evidence trace

The trace directly checks final-resume skills against:

- `reviewed_candidate_profile["skills"]`;
- `reviewed_candidate_profile["experience"][i]["skills"]`.

For the professional summary, it verifies that relevant reviewed-profile sections contain evidence. It does not semantically validate each summary sentence.

For experience, it verifies that reviewed experience exists. The section trace does not itself semantically validate each generated bullet.

### Partial experience-bullet validation

Generated experience bullets can contain `source_evidence_id`. The hallucination checker mainly tests:

- whether the linked evidence record exists;
- whether the bullet and linked evidence have meaningful keyword overlap.

This is partial claim-level machinery. It is not comprehensive semantic proof and does not cover every resume claim type.

---

## 13. Current Matching and Gap Logic

### Current matching

For each parsed required skill, the matcher:

1. normalizes the JD skill conservatively;
2. compares it with reviewed top-level skills;
3. compares it with skills attached to extracted evidence, including nested experience skills;
4. applies a small safe alias set;
5. preserves unmatched requirements as missing skills;
6. calculates a percentage based on matched versus required skills.

Examples of intended conservative behavior:

```text
Microsoft Office ↔ MS Office
Excel alone ≠ Microsoft Office
Excel alone ≠ CRM
client database ≠ CRM
explicitly negated CRM ≠ CRM evidence
```

Evidence ID mappings may be available for matches supported by extracted Evidence records. A top-level skill match does not necessarily receive an Evidence ID in `evidence_matches`.

### Current V1 gap behavior

- Every unmatched required skill becomes a critical gap.
- `minor_gaps` currently remains empty.
- Must-have versus preferred/nice-to-have classification is not built.
- Add-only-if-true and learning-gap treatments are product rules or roadmap concepts, not current structured gap-engine categories.
- Critical gaps feed career recommendations.
- Critical gaps do not independently block resume generation or DOCX download.

### Readiness tiers

The recommendation engine currently maps score to:

| Match score | Readiness tier |
|---|---|
| 90–100% | Ready to Apply |
| 70–89.99% | Apply with Minor Gaps |
| 40–69.99% | Targeted Upskilling Recommended |
| Below 40% | Significant Upskilling Required |

These labels do not override the evidence gates and do not guarantee job readiness.

---

## 14. Current DOCX Safety Gate

The real-flow DOCX download is gated in `app.py`. It is more than a direct exporter call.

### Current blockers

The gate blocks download when applicable if:

- no analysis result exists;
- the saved analysis baseline no longer matches current inputs;
- analysis did not complete;
- the upload/paste pipeline did not succeed;
- the analysis result is failed or partial;
- the final resume is missing;
- final-resume validation is missing or invalid;
- validation contains errors;
- the section-level evidence trace is missing or failed;
- final-resume skills include unsupported skills;
- the skills, professional-summary, or experience sections are marked unsupported.

A missing JD job-title trace alone does not block download because missing JD parsing evidence is not candidate hallucination.

### Meaning of stale analysis

Stale analysis means an analysis result whose saved input baseline no longer matches the current uploaded CV, reviewed profile, or pasted JD, including changes made in the same Streamlit session.

### What the gate proves

The gate proves that the result passed the currently implemented structural, freshness, pipeline, and evidence checks.

It does not prove:

- acceptance by an employer ATS;
- full semantic truth of every sentence;
- independent verification of user-entered information;
- comprehensive per-claim traceability;
- that the candidate meets every JD requirement.

### Export description

When the gate passes, the export adapter converts the final-resume structure into a DOCX payload and `python-docx` produces an ATS-friendly structured document. “ATS-friendly” describes formatting intent, not validation against all employer ATS products.

---

## 15. Current Testing Strategy

The repository has extensive unit, integration, regression, smoke, and real-flow fixture coverage.

**Current verified suite:** 505 passing tests with one pytest cache-write warning.

A strict one-test-module-per-engine mapping is not currently present.

### Covered behavior includes

- PDF and DOCX extraction behavior;
- malformed and unsupported input handling;
- candidate and JD parsing;
- language evidence routing;
- nested experience-skill extraction;
- negation guards;
- Microsoft Office alias behavior;
- CRM non-inference;
- matcher, scorer, and gap behavior;
- recommendation tiers;
- evidence extraction and evidence model behavior;
- summary, skills, and bullet generation contracts;
- hallucination-checker behavior;
- final-resume assembly and schema validation;
- section-level evidence trace;
- export adapter and DOCX generation;
- full-pipeline smoke tests;
- real-flow fixtures;
- Streamlit gate behavior, including stale and unsupported-skill blocking.

### Testing limits

- Passing tests do not prove that every real-world PDF layout parses correctly.
- Passing tests do not make section-level trace equivalent to claim-level proof.
- Automated tests do not replace manual inspection of DOCX content and formatting.
- The cache warning is not a test failure, but it should not be represented as a completely warning-free run.

---

## 16. Known Limitations

| # | Limitation | Current impact |
|---|---|---|
| 1 | Candidate schema is text-oriented rather than fully structured | Company, role, dates, and education are not canonical saved fields |
| 2 | Contact and education extraction are not retained in the reviewed profile | Data can be present in parser metadata but not downstream canonical state |
| 3 | Resume preview can concatenate skill labels | Low-severity display defect |
| 4 | Final skills can retain JD-style phrasing | Output-quality issue |
| 5 | Recommendations can be mechanically worded | Output-quality issue |
| 6 | Professional-summary trace is section-level | Individual summary claims are not semantically checked |
| 7 | Experience section trace is section-level | It does not itself verify every bullet |
| 8 | Bullet hallucination checking uses ID presence and keyword overlap | Partial validation, not semantic proof |
| 9 | No comprehensive per-claim trace | Incomplete explainability and safety coverage |
| 10 | No integrated persistent Master Profile | No durable career history |
| 11 | No persistent Evidence Ledger | No durable skill-to-source graph |
| 12 | No authentication or database | No accounts or cross-session persistence |
| 13 | No production deployment | Developer-machine use only |
| 14 | No OCR | Scanned-image PDFs are unsupported |
| 15 | English-focused parser/UI | Arabic and bilingual support are not built |
| 16 | JD title parsing is unreliable for some layouts | Job title may be absent |
| 17 | Must-have versus preferred classification is not built | Every unmatched required skill becomes critical |
| 18 | Certification parsing remains imperfect | Some blocks may collapse |
| 19 | Experience segmentation remains imperfect | Roles and bullets may merge or split incorrectly |
| 20 | Reference data remains limited | Coverage must expand without weakening determinism |
| 21 | Readiness labels are score bands only | They do not represent verified hiring readiness |
| 22 | No live Gemini real-flow generation | Current user flow remains deterministic |
| 23 | No learning roadmap or progress tracker | Gap advice is not yet an ordered development plan |
| 24 | No job, interview, salary, or market-intelligence modules in the user product | Career platform vision remains future work |

---

## 17. Corrections from PRD v2.0

PRD v2.1 corrects the following material issues:

1. Replaces the aspirational candidate schema with the actual six-key reviewed-profile schema.
2. Separates the current actual model from the future target Master Profile.
3. Corrects `final_resume_assembler.py` to `resume_output_assembler.py`.
4. Adds the scorer, gap analyzer, prompt builder, draft builder, export adapter, and AI response validator to the architecture.
5. Removes nonexistent `data/reference/tools.json`.
6. Adds existing `data/reference/certifications.json`.
7. Adds `matched_skills` and `strongest_skills` to the final-resume skills schema.
8. Corrects assembler metadata and includes `skills_source`.
9. Replaces universal no-invention enforcement claims with an accurate layered-control description.
10. Distinguishes direct skill support checking from section-level summary and experience trace.
11. Documents partial evidence-ID and keyword-overlap bullet validation without calling it comprehensive per-claim trace.
12. Corrects current gap behavior: all missing required skills are critical and `minor_gaps` remains empty.
13. Removes the inaccurate claim that critical gaps independently block DOCX download.
14. Corrects the hallucination checker from a universal claim validator to its current experience-bullet scope.
15. Distinguishes the built in-memory Evidence model from the unbuilt persistent Evidence Ledger.
16. Acknowledges preliminary static Master Profile artifacts without claiming an integrated Master Profile exists.
17. Replaces guaranteed ATS language with “ATS-oriented” and “ATS-friendly structured DOCX.”
18. Corrects stale-analysis wording to include same-session CV, reviewed-profile, and JD changes.
19. Replaces the one-test-file-per-engine claim with the verified 505-test suite description.
20. Clarifies that manually reviewed edits are user-confirmed, not independently verified.

---

## 18. Future Product Roadmap

### Phase 1 — Stabilize the safe resume MVP

**Current objective:** improve the existing local workflow without weakening evidence controls.

| Item | Status |
|---|---|
| Preview skill-spacing cleanup | Not built |
| Natural candidate wording for matched skills | Not built |
| Recommendation wording cleanup | Not built |
| JD job-title inference improvement | Not built |
| Must-have versus preferred classification | Not built |
| Certification parser improvement | Not built |
| Experience segmentation improvement | Not built |
| Expanded real-role fixtures | Partially built |
| DOCX formatting and styling improvement | Partially built |
| Manual end-to-end QA across representative UAE roles | Ongoing need |

### Phase 2 — Master Profile and Evidence Ledger

**Current objective:** replace session-only profile state with durable, user-controlled career evidence.

| Item | Status |
|---|---|
| Preliminary static Master Profile JSON | Exists; not integrated |
| Preliminary Master Profile schema draft | Exists; not canonical |
| In-memory Evidence model | Built |
| In-memory evidence extraction | Built |
| Integrated canonical Master Profile | Not built |
| Persistent per-user Master Profile | Not built |
| Persistent Evidence Ledger | Not built |
| Skill-to-source relationship store | Not built |
| Evidence editing and deletion workflow | Not built |
| Durable confidence and provenance model | Not built |
| Evidence explanation view | Not built |

### Phase 3 — Per-claim resume generation

**Current objective:** move from section-level coverage and partial bullet linkage to comprehensive claim-level support.

| Item | Status |
|---|---|
| Bullet `source_evidence_id` field | Built |
| Bullet evidence-ID existence check | Built |
| Bullet keyword-overlap check | Built |
| Every summary sentence linked to evidence IDs | Not built |
| Semantic validation of every experience bullet | Not built |
| Claim trace for skills, education, credentials, and dates | Not built |
| User-visible per-claim explanation | Not built |
| Universal claim-level blocking | Not built |
| Safer natural rewriting | Not built |
| Live Gemini real-flow integration | Not built |

### Phase 4 — Career Intelligence Layer

| Item | Status |
|---|---|
| Deep fit explanation beyond current score and lists | Not built |
| Gap prioritization | Not built |
| Must-have/nice-to-have weighting | Not built |
| Learning roadmap engine | Not built |
| UAE-relevant course and certification recommendations | Not built |
| Progress tracker | Not built |
| Certificate upload to update persistent evidence | Not built |
| Target-role readiness over time | Not built |

### Phase 5 — Platform and Product Layer

| Item | Status |
|---|---|
| Authentication | Not built |
| Supabase or other user database | Not built |
| Saved profiles, CVs, and analyses | Not built |
| Saved job descriptions | Not built |
| Job application tracker | Not built |
| Email reminders and nudges | Not built |
| Job opportunity discovery | Not built |
| Interview preparation | Not built |
| Salary insights | Not built |
| UAE labor-market intelligence | Not built |

### Phase 6 — Productionization

| Item | Status |
|---|---|
| Cloud deployment | Not built |
| Production security hardening | Not built |
| Production file-storage policy | Not built |
| Audit logs | Not built |
| Data-retention and deletion workflows | Not built |
| Error monitoring | Not built |
| Scalable multi-user architecture | Not built |
| Arabic and bilingual support | Not built |
| OCR for scanned CVs | Not built |

---

## 19. Non-Functional Requirements

The following are product requirements and targets. They are not all verified current characteristics.

### Safety and integrity

- Candidate facts must originate from reviewed user input and linked evidence.
- JD-only requirements must remain gaps or advice unless candidate evidence exists.
- Missing or uncertain evidence must be preserved as uncertainty, not repaired through invention.
- Safety controls must fail visibly and block export when a defined gate fails.
- Future AI integrations must retain deterministic validation and fallback paths.

### Performance targets

| Operation | Target |
|---|---|
| Text extraction | Under 3 seconds for normal supported files |
| Candidate parsing | Under 3 seconds |
| JD parsing | Under 2 seconds |
| Full deterministic analysis | Under 10 seconds |
| Future live AI generation | Under 15 seconds where practical |
| UI feedback | Loading state for operations exceeding 1 second |

These are targets; the current test suite does not establish production service-level guarantees.

### Reliability

- Malformed CV or JD input should return explicit errors or warnings.
- Empty required inputs should cause clean hard stops.
- Failed or partial analysis must not silently become download-ready.
- Export must not repair unsafe content to force a pass.
- Existing real-flow safety tests must remain regression protected.

### Maintainability

- Business rules should remain deterministic where possible.
- UI orchestration and engine logic should become more clearly separated over time.
- Reference data should be versioned and reviewable.
- Changes to evidence, matching, generation, or gates require proportional automated tests.
- Current full-suite status must be reported from an actual test run, not copied forward unverified.

### Scalability targets

- Future data models must support strict per-user isolation.
- Reference-taxonomy expansion should not require unsafe inference.
- Persistent evidence architecture must support multiple CVs and target roles without duplicating contradictory truth.

---

## 20. Security and Privacy Requirements

### Current local-MVP state

- No authentication is implemented.
- No user database is implemented.
- No persistent per-user profile is implemented.
- The application is not production deployed.
- CV and JD content is processed locally in the active application workflow.
- Temporary DOCX export files are implementation details and must be cleaned up after byte generation.

The absence of a database reduces some current persistence exposure, but it does not make the application production-secure.

### Requirements before public production use

- Authentication with an explicitly selected provider
- Strict per-user authorization and data isolation
- Secrets stored outside source control
- File-type, size, and content validation
- Encrypted transport and appropriate storage encryption
- Defined upload retention and deletion rules
- User-controlled account and data deletion
- Audit logging without exposing CV content or secrets
- Error monitoring with sensitive-data redaction
- Dependency and vulnerability management
- Privacy notice and consent appropriate to the operating jurisdictions
- Incident-response and recovery procedures

Gmail OAuth and Supabase are possible future choices, not committed current architecture.

---

## 21. Out of Scope for Current MVP

- Employer-to-candidate matching
- Company job posting
- Recruitment agency workflows
- Public candidate profiles or social networking
- Guaranteed ATS acceptance
- Employer ATS simulation
- Guaranteed interviews or placement
- Fabricated skills, credentials, metrics, or experience
- Persistent accounts and profiles
- Bulk CV processing
- Standalone grammar checking
- Salary negotiation coaching
- Live salary and market data
- Job opportunity discovery
- Application tracking
- Interview preparation
- Comprehensive learning roadmaps
- Arabic and bilingual parsing
- OCR for scanned documents

Some items are planned for later phases even though they are outside the current MVP.

---

## 22. Open Questions

| # | Question | Decision point |
|---|---|---|
| 1 | What is the final public product name? | Before public launch |
| 2 | What belongs in free versus paid plans? | Before commercial launch |
| 3 | Which authentication and database providers should be selected? | Before Phase 5 implementation |
| 4 | How should manually added user evidence be distinguished from CV-extracted evidence? | Before Master Profile design |
| 5 | What review state is required before evidence becomes generation-eligible? | Before Evidence Ledger implementation |
| 6 | How should contradictory or expired evidence be handled? | Before persistent evidence design |
| 7 | What confidence values are meaningful and how are they calculated? | Before durable confidence implementation |
| 8 | Should generation have a match-score threshold, or should evidence gates alone decide export? | Before changing current gate behavior |
| 9 | How should required versus preferred JD items be represented and weighted? | Before gap-engine V2 |
| 10 | Which UAE certifications and regulators are maintained in reference data? | Before taxonomy expansion |
| 11 | Should roadmaps name specific course providers or remain provider-neutral? | Before Phase 4 |
| 12 | What constitutes sufficient semantic support for a rewritten claim? | Before comprehensive claim trace |
| 13 | Should per-claim tracing precede or follow persistent Master Profile migration? | Phase 2/3 planning |
| 14 | At what phase is production deployment appropriate? | Roadmap governance |
| 15 | Is Arabic JD parsing required for the first public release? | Before production scope lock |

---

## 23. Glossary

| Term | Definition |
|---|---|
| `parsed_candidate_profile` | Raw deterministic parser output before user review. |
| `reviewed_candidate_profile` | User-reviewed profile held in Streamlit session state and used as the canonical candidate input for the real upload/paste flow. |
| User-confirmed evidence | Information the user has saved as true. It is not independently background-verified by the MVP. |
| Evidence | An in-memory structured record linking text and skills to a source item such as experience, project, certification, or achievement. |
| Evidence Ledger | Future persistent, user-editable store connecting claims and skills to durable source evidence. Not built. |
| Master Profile | Future integrated persistent career record. Static JSON/schema artifacts exist, but the functional per-user system is not built. |
| Closed candidate-evidence boundary | Rule that JD-only requirements cannot become candidate facts. |
| Match score | Deterministic percentage of parsed required skills matched by current candidate evidence. |
| Critical gap | In V1, any unmatched required skill. It does not independently block DOCX download. |
| Minor gap | A structured output field that currently remains empty because preferred-skill classification is not built. |
| Add only if true | Product guidance for a possible user-supplied fact; not a current structured gap-engine category. |
| Readiness tier | Score-band label produced by the recommendation engine, not a verified hiring decision. |
| Hallucination checker | Current experience-bullet validator using linked evidence IDs and keyword overlap. It is not universal claim verification. |
| Section-level evidence trace | Trace showing direct skill support and coarse evidence presence for summary and experience sections. |
| Comprehensive per-claim trace | Future capability linking and validating every generated claim against specific evidence. Not built. |
| DOCX safety gate | Current set of freshness, status, schema, evidence, and support checks controlling real-flow download. |
| Stale analysis | Analysis whose saved input baseline no longer matches the current CV, reviewed profile, or JD. |
| ATS-oriented | Designed with simple structured resume use in mind; not guaranteed or validated against every employer ATS. |
| Deterministic generation | Output produced through local rules and structured data without live generative-model calls. |
| Developer Sample Mode | A separate development/demo path that is not the canonical real-user evidence flow. |

---

## 24. Truthful Current Status Statement

The UAE Career Intelligence Platform is currently a local Streamlit resume-analysis and DOCX-generation MVP.

It has a working real-user flow:

```text
Upload CV
→ extract text
→ parse candidate profile
→ review and save profile
→ paste and parse JD
→ match and score
→ classify current V1 gaps
→ generate recommendations and resume components
→ assemble and validate final resume
→ build section-level evidence trace
→ apply the DOCX safety gate
→ download an ATS-friendly structured DOCX when allowed
```

The current verified automated suite contains **505 passing tests with one pytest cache-write warning**.

The product has layered deterministic no-invention controls. Final-resume skills receive direct candidate-support checks. Generated experience bullets have partial evidence-ID and keyword-overlap validation. Professional-summary and experience trace remains section-level and does not semantically verify every sentence or bullet.

The product correctly preserves unmatched JD requirements as gaps instead of candidate skills. In current V1 gap behavior, every unmatched required skill is classified as critical, `minor_gaps` remains empty, and critical gaps do not independently block DOCX download.

The current reviewed candidate profile is session-only and text-oriented. It is not the future structured Master Profile.

An in-memory Evidence model and extractor are built and tested. A preliminary static Master Profile JSON and schema draft also exist. There is still no integrated persistent Master Profile, persistent Evidence Ledger, user database, authentication, production deployment, comprehensive per-claim trace, or live Gemini generation in the real flow.

The product is therefore a real and tested safe-resume MVP, not yet the full UAE Career Intelligence Platform.

The next major architecture milestone is the integrated Master Profile and persistent Evidence Ledger. That evidence foundation should precede claims of comprehensive traceability or the expansion into broader career-intelligence features.

---

*PRD v2.1 is intended to be the repository-aligned product source of truth as of Sprint 66G. Future sprint claims, test counts, and implementation statuses must be reverified against the repository before this document is updated.*
