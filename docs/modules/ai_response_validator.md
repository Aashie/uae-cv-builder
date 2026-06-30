# AI Response Validator

## Objective

Validate AI-generated responses before they reach the Hallucination Checker.

The validator performs structural validation only.
It does NOT determine whether claims are true.
Its responsibility is to ensure the response conforms to the AI Generation Contract.

---

## Deliverable

Files:

- engine/ai_response_validator.py
- tests/test_ai_response_validator.py

---

## Inputs

AI Output Schema:

```json
{
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
```

---

## Outputs

```json
{
  "is_valid": false,
  "errors": []
}
```

The validator runs in collect-all mode.
All errors are gathered in a single pass and returned together.
It does not stop at the first failure.

---

## Validation Rules

### Supported Top-Level Fields

```
summary
experience_bullets
skills
```

Any field outside this set is unsupported and must be flagged.

### Required Top-Level Keys

- summary
- experience_bullets
- skills

### Required Skill Keys

- technical
- soft
- domain

### Checks

1. Required top-level keys exist.
2. Correct data types throughout.
3. summary must not be empty.
4. experience_bullets must be a list.
5. Every item in experience_bullets must be a dict.
6. Every bullet dict must contain: text and source_evidence_id.
7. Bullet text must not be empty.
8. source_evidence_id must not be empty.
   Note: This validator confirms source_evidence_id is present and non-empty.
   It does NOT verify the ID resolves to an existing evidence record.
   That check belongs to the Hallucination Checker.
9. skills must be a dict.
10. technical, soft, and domain must each be a list.
11. No unsupported top-level fields.

---

## Output Format

Valid:

```json
{
  "is_valid": true,
  "errors": []
}
```

Invalid:

```json
{
  "is_valid": false,
  "errors": [
    "Missing required field: summary",
    "Missing required field: source_evidence_id in bullet at index 0"
  ]
}
```

---

## Success Criteria

- Detects missing keys.
- Detects invalid types.
- Detects empty values.
- Detects unsupported top-level fields.
- Detects non-dict items inside experience_bullets.
- Returns all errors in a single pass.
- Returns deterministic, human-readable error messages.

---

## Tests

- Valid response passes all checks
- Missing summary
- Missing experience_bullets
- Missing skills
- Empty summary
- experience_bullets is not a list
- Bullet item is not a dict
- Missing bullet text
- Missing source_evidence_id
- Empty bullet text
- Empty source_evidence_id
- skills is not a dict
- technical is not a list
- soft is not a list
- domain is not a list
- Unsupported top-level field present
- Multiple validation errors returned in single pass

---

## Commit

```
git commit -m "Add AI Response Validator"
```