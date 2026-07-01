# Resume Analysis Orchestrator Integration Update

## Objective

Update the existing Resume Analysis Orchestrator so it integrates the completed AI-safe resume generation modules.

Sprint 20 connects:

- Professional Summary Generator
- Experience Bullet Generator
- AI Response Validator
- Hallucination Checker
- Resume Output Assembler

into the main resume analysis pipeline.

The orchestrator becomes the single backend entry point that produces both analysis intelligence and a final structured resume object.

---

## Deliverable

Files:

- engine/resume_analysis_orchestrator.py
- tests/test_resume_analysis_orchestrator.py

No new orchestrator should be created.

No changes should be made to:

- engine/ai_response_validator.py
- engine/experience_bullet_generator.py
- engine/resume_output_assembler.py
- engine/hallucination_checker.py
- engine/professional_summary_generator.py

Reason:

These modules are already completed and tested.

Sprint 20 only integrates them.

---

## Locked Decisions

```text
Q1 = A  Update existing Resume Analysis Orchestrator only
Q2 = A  Call Experience Bullet Generator after Resume Draft Builder
Q3 = A  Call Resume Output Assembler at the end
Q4 = A  Validate bullet output with context="experience_bullets"
Q5 = A  Hallucination Checker runs on experience bullets only
Q6 = A  Bullet validation failure means partial status + empty bullets + continue
Q7 = A  Hallucination failure means use passed bullets only + partial
Q8 = A  Do not modify Resume Output Assembler
```

---

## Existing Stable Baseline

Before Sprint 20:

```text
189/189 tests passing
```

Completed modules already available:

- Evidence Extractor
- Career Insights Engine
- Matcher Engine
- Scoring Engine
- Skill Gap Analyzer
- Recommendation Engine
- Prompt Builder
- Resume Draft Builder
- Professional Summary Generator
- AI Response Validator
- Hallucination Checker
- Experience Bullet Generator
- Resume Output Assembler

---

## Public Function

Existing function remains:

```python
run_resume_analysis(profile: dict, job_description) -> dict
```

Do not rename this function.

Do not create a second orchestrator.

---

## Updated Pipeline

```text
Evidence Extractor
↓
Career Insights Engine
↓
Matcher
↓
Scorer
↓
Skill Gap Analyzer
↓
Recommendation Engine
↓
Prompt Builder
↓
Resume Draft Builder
↓
Professional Summary Generator
↓
AI Response Validator
↓
Experience Bullet Generator
↓
AI Response Validator with context="experience_bullets"
↓
Hallucination Checker for experience_bullets only
↓
Resume Output Assembler
↓
Final Orchestrator Output
```

---

## Career Insights Order

Career Insights Engine remains immediately after Evidence Extractor.

Reason:

Career Insights Engine uses Evidence objects only.

Expected input:

```python
analyze_career_insights(evidence_items)
```

It does not require:

- match score
- skill gaps
- recommendations
- prompt package
- resume draft

Therefore the correct order is:

```text
Evidence Extractor
↓
Career Insights Engine
↓
Matcher
```

---

## Validator Context Requirement

Sprint 18 already updated AI Response Validator to support:

```python
validate_ai_response(response, context="experience_bullets")
```

Sprint 20 must not modify the validator unless a precondition check proves this context is missing.

Expected behavior:

```python
validate_ai_response(
    experience_bullet_output["ai_output"],
    context="experience_bullets"
)
```

In this context:

- empty summary is allowed
- empty skills lists are allowed
- experience_bullets must still be valid
- every bullet must have non-empty text
- every bullet must have non-empty source_evidence_id

---

## Professional Summary Validation

Professional Summary Generator returns:

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

Validate using default context:

```python
validate_ai_response(professional_summary_output)
```

If validation passes:

```text
Use professional_summary_output.
```

If validation fails:

```text
Mark orchestrator status partial.
Use resume_draft professional_summary through Resume Output Assembler fallback.
Continue pipeline.
```

---

## Experience Bullet Generation

Call:

```python
generate_experience_bullets(evidence_items)
```

Expected output:

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

If Experience Bullet Generator returns failed status:

```text
Mark orchestrator status partial.
Use empty experience bullets.
Continue to Resume Output Assembler.
```

---

## Experience Bullet Validation

Validate using:

```python
validate_ai_response(
    experience_bullet_output["ai_output"],
    context="experience_bullets"
)
```

If validation passes:

```text
Continue to Hallucination Checker.
```

If validation fails:

```text
Mark orchestrator status partial.
Add validation errors.
Replace experience_bullet_output["ai_output"]["experience_bullets"] with [].
Continue to Resume Output Assembler.
```

---

## Hallucination Checker Scope

Hallucination Checker in V1 covers:

```text
experience_bullets only
```

It does not check:

- professional summary
- skills
- job title
- recommendations
- career insights

Professional summary passes through AI Response Validator but is not checked by Hallucination Checker in V1.

Summary hallucination detection is deferred to V2.

---

## Hallucination Checker Rule

Run Hallucination Checker only after bullet validation passes.

Call:

```python
check_hallucinations(
    experience_bullet_output["ai_output"],
    evidence_items
)
```

If hallucination count is 0:

```text
Use all bullets.
```

If hallucination count is greater than 0:

```text
Mark orchestrator status partial.
Add error: "Hallucination checker removed unsupported bullets."
Use only hallucination_check["passed_bullets"].
Discard failed bullets from final resume assembly.
Continue pipeline.
```

If all bullets fail:

```text
Use empty bullets.
Mark partial.
Continue pipeline.
```

---

## Resume Output Assembler Integration

Call:

```python
assemble_resume_output(
    resume_draft,
    professional_summary_output_for_assembler,
    experience_bullet_output_for_assembler
)
```

Where:

```text
professional_summary_output_for_assembler
```

is either:

- valid Professional Summary Generator output, or
- a structure that allows Resume Output Assembler to fall back to resume_draft["professional_summary"]

And:

```text
experience_bullet_output_for_assembler
```

contains only validated and hallucination-approved bullets.

The orchestrator must not modify Resume Output Assembler.

---

## Final Orchestrator Output Schema

Keep existing Sprint 17 output fields.

Add final resume assembly fields.

Expected output:

```python
{
    "status": "",
    "errors": [],

    "match_score": 0,
    "matched_skills": [],
    "missing_skills": [],

    "skill_gaps": {
        "critical_gaps": [],
        "minor_gaps": []
    },

    "recommendations": {
        "resume_recommendations": [],
        "career_recommendations": []
    },

    "readiness_tier": "",

    "career_insights": {},

    "resume_draft": {},

    "summary": "",

    "ai_validation": {
        "is_valid": False,
        "errors": []
    },

    "experience_bullet_output": {},

    "experience_bullet_validation": {
        "is_valid": False,
        "errors": []
    },

    "hallucination_check": {
        "passed_bullets": [],
        "failed_bullets": [],
        "hallucination_count": 0
    },

    "resume_output": {
        "status": "",
        "errors": [],
        "final_resume": {}
    },

    "final_resume": {}
}
```

---

## Status Rules

### success

Use when:

- all required modules complete
- summary validation passes
- experience bullet generation succeeds
- experience bullet validation passes
- hallucination count is 0
- resume output assembly succeeds
- errors list is empty

---

### partial

Use when pipeline continues but recoverable issues occur.

Examples:

- career insights failure
- recommendation failure
- professional summary validation failure
- experience bullet generator failed
- experience bullet validation failed
- hallucination checker removed bullets
- resume output assembler returned partial

---

### failed

Use only for hard stops or required module failures.

Existing hard stops remain:

- profile is None
- profile is empty
- job_description is None
- job_description.required_skills missing or empty

No downstream modules should execute after hard stop.

---

## Error Handling

Use deterministic, human-readable errors.

Recommended Sprint 20 errors:

```text
Professional summary validation failed: <errors>
Experience bullet generation failed.
Experience bullet validation failed: <errors>
Hallucination checker removed unsupported bullets.
Resume output assembly returned partial status.
Resume output assembly failed.
```

Existing errors from Sprint 17 should remain.

---

## No Changes To Completed Modules

Sprint 20 must not modify:

- AI Response Validator
- Experience Bullet Generator
- Resume Output Assembler
- Hallucination Checker
- Professional Summary Generator
- Resume Draft Builder
- Prompt Builder
- Matcher
- Scorer
- Skill Gap Analyzer
- Recommendation Engine
- Career Insights Engine
- Evidence Extractor

Only the orchestrator and orchestrator tests should change.

---

## No Search Grounding

Sprint 20 does not use Search Grounding.

Candidate resume generation remains closed-universe and evidence-based.

Search Grounding remains restricted to market-context outputs only.

---

## Not Included In Sprint 20

Sprint 20 does not include:

- real Gemini API integration
- new AI generation
- summary hallucination detection
- skills section generation
- export engine
- Streamlit UI
- DOCX/PDF generation
- application tracker
- skills vault
- profile intelligence V2

---

## Tests

Required tests:

- successful orchestrator pipeline includes final_resume
- orchestrator calls Experience Bullet Generator
- orchestrator validates experience bullets with context="experience_bullets"
- orchestrator runs Hallucination Checker after bullet validation
- orchestrator calls Resume Output Assembler
- final_resume exists in orchestrator output
- resume_output exists in orchestrator output
- experience_bullet_output exists in orchestrator output
- experience_bullet_validation exists in orchestrator output
- hallucination_check exists in orchestrator output
- professional summary validation failure marks partial
- experience bullet generator failure marks partial
- experience bullet validation failure marks partial
- bullet validation failure uses empty bullets
- hallucination failure marks partial
- hallucination failure passes only passed bullets to assembler
- all hallucinated bullets results in empty bullets
- assembler partial status marks orchestrator partial
- assembler failed status marks orchestrator partial or failed based on failure reason
- existing hard stops still work
- existing Sprint 17 tests still pass or are updated only if output schema expanded
- Career Insights still runs immediately after Evidence Extractor
- AI Response Validator is not modified
- Experience Bullet Generator is not modified
- Resume Output Assembler is not modified
- Hallucination Checker is not modified

---

## Success Criteria

Sprint 20 is complete when:

- Existing Resume Analysis Orchestrator is updated
- No second orchestrator is created
- Experience Bullet Generator is integrated
- Experience bullets are validated with context="experience_bullets"
- Hallucination Checker runs on experience bullets only
- Failed bullets are removed before final resume assembly
- Resume Output Assembler is integrated
- final_resume is included in orchestrator output
- Existing hard stops still work
- Partial behavior remains stable
- Completed modules are not modified
- All Sprint 20 tests pass
- Full suite passes

---

## Commit

```bash
git commit -m "Integrate Resume Output Pipeline"
```