# Resume Output Assembler

## Objective

Build a deterministic Resume Output Assembler.

The assembler combines already-generated, already-validated resume components into one final structured resume object.

It does not generate new content.

It does not call AI providers.

It does not rewrite candidate claims.

It does not perform hallucination checking.

It only organizes safe upstream outputs into a final resume-ready structure.

---

## Deliverable

Files:

- engine/resume_output_assembler.py
- tests/test_resume_output_assembler.py

Controlled documentation update:

- docs/modules/ai_generation_contract.md

Reason:

Add a permanent Search Grounding boundary:

Search Grounding applies only to market-context outputs such as UAE job trends, salary insights, industry demand, and hiring trend summaries.

Search Grounding must never be applied to candidate-data generation such as summaries, bullets, skills, credentials, achievements, or resume claims.

---

## Locked Decisions

```text
Q1 = A  Accept already-generated outputs only
Q2 = A  Return wrapper with status/errors/final_resume
Q3 = A  AI summary first, resume_draft fallback, empty string + partial if unavailable
Q4 = A  Use experience_bullet_output["ai_output"]["experience_bullets"]
Q5 = A  Use resume_draft["key_skills"] and resume_draft["matched_skills"]
Q6 = A  No hallucination checking inside assembler
Q7 = A  Structured final_resume object with metadata
Q8 = A  Hard stop only if resume_draft is missing or empty
```

---

## Public Function

```python
assemble_resume_output(
    resume_draft: dict,
    professional_summary_output: dict,
    experience_bullet_output: dict
) -> dict
```

---

## Inputs

### resume_draft

Expected from Resume Draft Builder.

Required base input.

Expected fields:

```python
{
    "job_title": "",
    "professional_summary": "",
    "key_skills": [],
    "matched_skills": [],
    "resume_bullets": []
}
```

---

### professional_summary_output

Expected from Professional Summary Generator.

Expected shape:

```python
{
    "summary": "",
    "experience_bullets": [],
    "skills": {
        "technical": [],
        "soft": [],
        "domain": []
    }
}
```

The assembler uses:

```python
professional_summary_output["summary"]
```

If unavailable, failed, None, or empty, fallback to:

```python
resume_draft["professional_summary"]
```

---

### experience_bullet_output

Expected from Experience Bullet Generator.

Expected wrapper shape:

```python
{
    "status": "success",
    "errors": [],
    "provider": "gemini",
    "mode": "deterministic",
    "ai_output": {
        "summary": "",
        "experience_bullets": [
            {
                "text": "",
                "source_evidence_id": ""
            }
        ],
        "skills": {
            "technical": [],
            "soft": [],
            "domain": []
        }
    }
}
```

The assembler uses:

```python
experience_bullet_output["ai_output"]["experience_bullets"]
```

---

## Output Wrapper Schema

The public function returns:

```python
{
    "status": "success",
    "errors": [],
    "final_resume": {
        "job_title": "",
        "professional_summary": "",
        "skills": {
            "key_skills": [],
            "matched_skills": []
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
            "bullet_source": ""
        }
    }
}
```

---

## Final Resume Schema

```python
{
    "job_title": "",
    "professional_summary": "",
    "skills": {
        "key_skills": [],
        "matched_skills": []
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
        "summary_source": "ai_generated | deterministic_fallback | empty",
        "bullet_source": "ai_generated | deterministic_evidence | empty"
    }
}
```

---

## Status Values

### success

Returned when:

- resume_draft exists
- summary is available from professional_summary_output or resume_draft
- experience bullets are available from experience_bullet_output
- skills are available from resume_draft
- no recoverable errors occurred

```python
status = "success"
errors = []
```

---

### partial

Returned when:

- resume_draft exists
- final_resume can still be assembled
- one or more recoverable issues occurred

Examples:

- professional_summary_output is None
- professional_summary_output has failed status
- professional_summary_output summary is empty
- resume_draft professional_summary is missing
- experience_bullet_output is None
- experience_bullet_output has failed status
- experience_bullet_output ai_output is missing
- experience_bullet_output experience_bullets are missing
- resume_draft key_skills is missing
- resume_draft matched_skills is missing

```python
status = "partial"
errors != []
```

---

### failed

Returned only when:

- resume_draft is None
- resume_draft is empty

```python
status = "failed"
```

No meaningful final resume can be assembled.

---

## Hard Stop Conditions

Hard stop only when:

```python
resume_draft is None
```

or:

```python
resume_draft == {}
```

Return:

```python
{
    "status": "failed",
    "errors": ["Resume draft is missing or empty."],
    "final_resume": {
        "job_title": "",
        "professional_summary": "",
        "skills": {
            "key_skills": [],
            "matched_skills": []
        },
        "experience_bullets": [],
        "metadata": {
            "assembled_by": "resume_output_assembler",
            "version": "v1",
            "summary_source": "empty",
            "bullet_source": "empty"
        }
    }
}
```

No further assembly should occur after hard stop.

---

## Summary Assembly Rule

Priority order:

```text
1. professional_summary_output["summary"]
2. resume_draft["professional_summary"]
3. ""
```

If professional_summary_output is None:

```text
Use resume_draft["professional_summary"]
Mark status partial.
Add error.
```

If professional_summary_output has:

```python
{"status": "failed"}
```

Use resume_draft fallback.

If both AI summary and resume_draft summary are missing or empty:

```text
Use ""
Mark status partial.
```

---

## Summary Source Metadata

Set:

```python
summary_source = "ai_generated"
```

when professional_summary_output contains a non-empty summary.

Set:

```python
summary_source = "deterministic_fallback"
```

when resume_draft["professional_summary"] is used.

Set:

```python
summary_source = "empty"
```

when no summary is available.

---

## Experience Bullet Assembly Rule

Use:

```python
experience_bullet_output["ai_output"]["experience_bullets"]
```

If experience_bullet_output is None:

```text
Use []
Mark status partial.
Add error.
```

If experience_bullet_output["status"] == "failed":

```text
Use []
Mark status partial.
Add error.
```

If experience_bullet_output["ai_output"] is missing:

```text
Use []
Mark status partial.
Add error.
```

If experience_bullet_output["ai_output"]["experience_bullets"] is missing:

```text
Use []
Mark status partial.
Add error.
```

If bullets exist:

```text
Preserve bullet text exactly.
Preserve source_evidence_id exactly.
Do not rewrite.
Do not remove source_evidence_id.
Do not add new bullets.
```

---

## Bullet Source Metadata

Set:

```python
bullet_source = "ai_generated"
```

when experience_bullet_output provides bullets from a future real AI mode.

Set:

```python
bullet_source = "deterministic_evidence"
```

when experience_bullet_output provides deterministic evidence-based bullets.

Set:

```python
bullet_source = "empty"
```

when no bullets are available.

Sprint 18 currently uses deterministic evidence-based bullets.

---

## Skills Assembly Rule

Use only resume_draft skills:

```python
resume_draft["key_skills"]
resume_draft["matched_skills"]
```

Do not use:

```python
professional_summary_output["skills"]
experience_bullet_output["ai_output"]["skills"]
```

Reason:

Sprint 18 intentionally leaves AI skill lists empty.

Skills should come from deterministic draft and matching outputs.

If key_skills is missing:

```text
Use []
Mark partial.
Add error.
```

If matched_skills is missing:

```text
Use []
Mark partial.
Add error.
```

---

## Job Title Rule

Use:

```python
resume_draft["job_title"]
```

If missing:

```text
Use ""
Mark partial.
Add error.
```

---

## No Content Generation Rule

The assembler must not generate new text.

Forbidden:

- no AI calls
- no Gemini calls
- no prompt building
- no rewriting
- no summarizing
- no bullet generation
- no skill generation
- no guessing missing values
- no inventing candidate claims

Allowed:

- copying safe values
- organizing safe values
- applying deterministic fallback paths
- setting metadata
- collecting errors

---

## No Hallucination Checking Rule

The assembler does not run hallucination checks.

Reason:

Hallucination checking belongs before final assembly.

The assembler trusts only pre-validated upstream outputs.

The assembler must preserve source evidence IDs so downstream export or audit tools can trace claims.

---

## Search Grounding Boundary

Search Grounding is not used in Sprint 19.

Permanent boundary:

```text
Search Grounding applies only to market-context outputs:
- UAE job trends
- salary insights
- industry demand
- hiring trend summaries

Search Grounding is never applied to candidate-data generation:
- professional summaries
- experience bullets
- skills
- credentials
- achievements
- resume claims
```

This protects the closed-universe evidence rule.

Candidate resume content must remain traceable to evidence already inside the system.

---

## Error Messages

Use deterministic human-readable error messages.

Recommended messages:

```text
Resume draft is missing or empty.
Professional summary output is missing.
Professional summary output failed.
Professional summary missing; used resume draft fallback.
Professional summary missing from all sources.
Experience bullet output is missing.
Experience bullet output failed.
Experience bullet ai_output is missing.
Experience bullets missing; used empty list.
Resume draft key_skills missing; used empty list.
Resume draft matched_skills missing; used empty list.
Resume draft job_title missing; used empty string.
```

---

## Not Included In Sprint 19

Sprint 19 does not include:

- AI generation
- real Gemini integration
- prompt building
- hallucination checking
- validation of AI output
- evidence extraction
- matching
- scoring
- recommendation generation
- Markdown export
- TXT export
- DOCX export
- PDF export
- Streamlit UI
- Application Tracker
- Skills Vault

---

## Tests

Required tests:

- successful assembly
- output wrapper contains status, errors, final_resume
- final_resume contains job_title
- final_resume contains professional_summary
- final_resume contains skills
- final_resume contains experience_bullets
- final_resume contains metadata
- uses professional_summary_output summary first
- falls back to resume_draft professional_summary
- empty summary from all sources marks partial
- None professional_summary_output marks partial
- failed professional_summary_output marks partial
- uses experience_bullet_output ai_output experience_bullets
- None experience_bullet_output marks partial
- failed experience_bullet_output marks partial
- missing ai_output marks partial
- missing experience_bullets marks partial
- preserves source_evidence_id
- preserves bullet text exactly
- uses resume_draft key_skills
- uses resume_draft matched_skills
- missing key_skills uses empty list and marks partial
- missing matched_skills uses empty list and marks partial
- missing job_title uses empty string and marks partial
- hard stop when resume_draft is None
- hard stop when resume_draft is empty
- does not call Professional Summary Generator
- does not call Experience Bullet Generator
- does not call Hallucination Checker
- metadata includes assembled_by
- metadata includes version
- metadata includes summary_source
- metadata includes bullet_source
- success status returned when no errors
- partial status returned when recoverable errors exist
- failed status returned when hard stop occurs
- output schema remains stable

---

## Success Criteria

Sprint 19 is complete when:

- Resume Output Assembler exists
- It accepts generated outputs only
- It does not call generators internally
- It does not call AI
- It does not run hallucination checker
- It assembles final_resume deterministically
- It preserves source_evidence_id
- It preserves bullet text exactly
- It uses AI summary first
- It falls back to resume_draft summary
- It uses experience_bullet_output bullets
- It uses resume_draft skills
- It returns stable wrapper output
- It supports success, partial, and failed states
- It records summary_source
- It records bullet_source
- It includes Search Grounding boundary in the AI contract documentation
- All Sprint 19 tests pass
- Full test suite passes

---

## Commit

```bash
git commit -m "Add Resume Output Assembler"
```