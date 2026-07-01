# Experience Bullet Generator

## Objective

Build an evidence-safe Experience Bullet Generator.

The generator creates resume-ready experience bullets from Evidence objects only.

It must not use raw profile data.

It must not invent achievements, metrics, job titles, tools, companies, certifications, or responsibilities that are not present in evidence.

---

## Deliverable

Files:

- engine/experience_bullet_generator.py
- tests/test_experience_bullet_generator.py

Controlled supporting update:

- engine/ai_response_validator.py
- tests/test_ai_response_validator.py

Reason for validator update:

The Experience Bullet Generator returns the full AI Generation Contract schema inside `ai_output`.

However, in this module:

- `summary` is intentionally empty
- `skills.technical` is intentionally empty
- `skills.soft` is intentionally empty
- `skills.domain` is intentionally empty

Therefore the validator must support a context/mode for experience bullet generation.

The default validator behavior must remain unchanged for full resume validation.

---

## Locked Decisions

```text
Q1 = A  Full AI Generation Contract schema inside ai_output
Q2 = A  Evidence objects only
Q3 = B  Maximum 5 bullets
Q4 = B  Deterministic evidence-based output
Q5 = A  Provider dispatcher exists, real Gemini not wired yet
Q6 = A  Experience evidence only
```

---

## Public Function

```python
generate_experience_bullets(
    evidence_items: list,
    provider: str = "gemini"
) -> dict
```

---

## Output Wrapper Schema

The public function returns a wrapper:

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

---

## AI Output Schema

The inner `ai_output` must follow the existing AI Generation Contract:

```python
{
    "summary": "",
    "experience_bullets": [
        {
            "text": "Coordinated field survey teams and managed mapping project schedules.",
            "source_evidence_id": "EXP001"
        }
    ],
    "skills": {
        "technical": [],
        "soft": [],
        "domain": []
    }
}
```

Important:

When called from Experience Bullet Generator:

- `summary` is empty by design
- `skills.technical` is empty by design
- `skills.soft` is empty by design
- `skills.domain` is empty by design

The validator must not reject empty summary or empty skills in this context.

---

## Validator Context Update

Existing validator behavior:

```python
validate_ai_response(response)
```

must continue to behave exactly as before.

Default context:

```python
context = "full_resume"
```

In default/full resume context:

- missing summary is invalid
- empty summary is invalid
- missing experience_bullets is invalid
- invalid bullet structure is invalid
- missing skills object is invalid
- unsupported top-level fields are invalid

New context:

```python
validate_ai_response(response, context="experience_bullets")
```

In experience bullet context:

- `summary` key is still required
- empty summary is allowed
- `experience_bullets` key is required
- `experience_bullets` must be a list
- every bullet must be a dict
- every bullet must contain non-empty `text`
- every bullet must contain non-empty `source_evidence_id`
- `skills` key is still required
- `skills.technical`, `skills.soft`, and `skills.domain` are required
- empty skill lists are allowed
- unsupported top-level fields are still invalid

Backward compatibility rule:

Existing tests for `validate_ai_response(response)` must still pass unchanged.

---

## Evidence Source

The generator uses Evidence objects only.

Allowed input:

```python
evidence_items
```

Forbidden input:

```python
profile
master_profile
raw_profile
profile_json
```

The generator must not read from files.

The generator must not load JSON.

The generator must not call the data loader.

---

## Evidence Filtering

Use only evidence items where:

```python
evidence.category.lower() == "experience"
```

Ignore:

- projects
- certifications
- achievements
- education
- skills-only evidence
- any non-experience category

---

## Usable Evidence Rule

An experience evidence item is usable only if it has:

- a non-empty `id`
- a non-empty `text`
- category equal to `experience`

Evidence without usable text must be skipped.

---

## Selection Rule

If more than 5 usable experience evidence items exist:

```text
Select the first 5 usable experience evidence items
as ordered in the evidence list.
```

No ranking.

No scoring.

No AI-based selection.

No evidence weighting in V1.

If 1–4 usable experience evidence items exist:

```text
Generate bullets for all available items.
```

No padding.

No fake bullets.

If 0 usable experience evidence items exist:

```python
{
    "status": "failed",
    "errors": ["No experience evidence found. Cannot generate bullets."],
    "provider": "gemini",
    "mode": "deterministic",
    "ai_output": {
        "summary": "",
        "experience_bullets": [],
        "skills": {
            "technical": [],
            "soft": [],
            "domain": []
        }
    }
}
```

---

## Provider Design

Sprint 18 uses a provider dispatcher.

Public function:

```python
generate_experience_bullets(evidence_items, provider="gemini")
```

Internal provider function:

```python
_generate_with_gemini(evidence_items)
```

Important:

In Sprint 18, Gemini is not wired to a real API.

The Gemini provider path directly calls the deterministic bullet builder.

Therefore:

```text
The deterministic builder is the primary implementation in Sprint 18.
It is not merely a fallback.
```

The retry/fallback architecture remains available for future real Gemini integration.

Unsupported providers should raise:

```python
ValueError
```

---

## Deterministic Bullet Builder

The deterministic builder converts each selected experience evidence item into one bullet.

Rules:

- one bullet per selected evidence item
- maximum 5 bullets
- use only evidence text
- preserve evidence meaning
- do not invent metrics
- do not invent tools
- do not invent company names
- do not invent job titles
- do not invent outcomes
- do not invent responsibilities
- do not exaggerate
- do not use raw profile data

Each bullet must include:

```python
{
    "text": "...",
    "source_evidence_id": "EXP001"
}
```

The bullet text must be short, resume-ready, and evidence-based.

Recommended maximum length:

```text
35 words
```

---

## Hallucination Safety

Generated bullets must be compatible with the existing Hallucination Checker.

Each bullet must include a valid `source_evidence_id`.

Each bullet must preserve enough meaningful keywords from the linked evidence text so that V1 keyword-overlap checking can pass.

The hallucination checker itself is not modified in Sprint 18.

---

## Hard Stop Conditions

Return failed wrapper output when:

- evidence_items is None
- evidence_items is empty
- no usable experience evidence exists

Error message:

```text
No experience evidence found. Cannot generate bullets.
```

---

## Failure Behavior

### Unsupported provider

Raise:

```python
ValueError
```

### No experience evidence

Return failed wrapper output.

### Empty or unusable experience evidence

Return failed wrapper output.

### Unexpected provider failure

In future real-AI mode, fallback to deterministic evidence-based bullets.

In Sprint 18, deterministic output is the primary path.

---

## Not Included In Sprint 18

Sprint 18 does not include:

- real Gemini API call
- prompt engineering for Gemini
- retry timing
- rate limit handling
- API key loading
- skills section generation
- summary generation
- project bullet generation
- certification bullet generation
- Streamlit UI
- export engine
- orchestrator integration

---

## Tests

Required tests:

- successful bullet generation
- output wrapper contains status, errors, provider, mode, ai_output
- ai_output follows AI Generation Contract shape
- summary is empty by design
- skills lists are empty by design
- validator accepts empty summary in experience_bullets context
- validator default context still rejects empty summary
- uses Evidence objects only
- filters only experience evidence
- ignores project evidence
- ignores certification evidence
- ignores achievement evidence
- generates maximum 5 bullets
- selects first 5 usable experience evidence items by list order
- generates all bullets when 1–4 usable experience items exist
- no padding when fewer than 5 items exist
- zero experience evidence returns failed status
- None evidence_items returns failed status
- empty evidence_items returns failed status
- bullet includes source_evidence_id
- bullet text is non-empty
- unsupported provider raises ValueError
- deterministic Gemini provider path works without real API call
- generated bullets pass hallucination checker when evidence overlap exists
- hallucination checker is not modified
- existing AI validator tests still pass

---

## Success Criteria

Sprint 18 is complete when:

- Experience Bullet Generator exists
- It uses Evidence objects only
- It generates only experience bullets
- It generates maximum 5 bullets
- It selects first 5 usable experience evidence items by list order
- It returns failed output when no usable experience evidence exists
- It returns wrapper output with inner AI Generation Contract schema
- Validator supports `context="experience_bullets"`
- Validator default behavior remains unchanged
- Generated bullets include source_evidence_id
- Generated bullets are hallucination-checker compatible
- No real Gemini API is required
- All Sprint 18 tests pass
- Full test suite passes

---

## Commit

```bash
git commit -m "Add Experience Bullet Generator"
```