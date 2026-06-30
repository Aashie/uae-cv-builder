# Professional Summary Generator

## Objective

Generate a professional summary using AI while preserving the evidence-based architecture of the platform.

This is the first AI generation module.

---

## Deliverable

Files:

- engine/professional_summary_generator.py
- tests/test_professional_summary_generator.py

---

## Inputs

Prompt Package

Resume Draft

Provider Name

---

## Outputs

Full AI Output Schema:

{
  "summary": "",
  "experience_bullets": [],
  "skills": {
    "technical": [],
    "soft": [],
    "domain": []
  }
}

---

## V1 Scope

V1 generates summary only.

experience_bullets must be an empty list.

skills must contain:

- technical: []
- soft: []
- domain: []

---

## Hallucination Scope

The summary has no source_evidence_id.

Therefore:

- AI Response Validator checks summary structure.
- Hallucination Checker does not check summary in V1.
- Summary hallucination detection is deferred to V2.

---

## Provider Architecture

V1 uses a function dispatcher:

generate_professional_summary(prompt_package, resume_draft, provider="gemini")

Provider dispatch:

- gemini → Gemini summary generation
- unsupported provider → ValueError

No class hierarchy in V1.

---

## Retry and Fallback

Retry once on:

- invalid JSON
- missing required keys
- empty response

No retry on:

- timeout
- authentication failure
- rate limit error

Retry delay:

2 seconds

Fallback:

Use deterministic summary from resume_draft.

Never surface broken AI output to user.

---

## Success Criteria

- Uses provider dispatcher.
- Returns full AI output schema.
- Generates summary only.
- Leaves experience_bullets empty.
- Leaves skills empty.
- Supports deterministic fallback.
- Raises error for unsupported provider.
- Does not call Hallucination Checker for summary.

---

## Tests

- Gemini provider path
- Unsupported provider raises ValueError
- Valid AI response returns full schema
- Invalid response falls back
- Missing summary falls back
- Empty response falls back
- experience_bullets remains empty
- skills remain empty
- fallback uses resume_draft summary

---

## Commit

git commit -m "Add Professional Summary Generator"