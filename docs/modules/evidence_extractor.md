# Evidence Extractor

## Objective

Convert profile data into structured Evidence objects.

The Evidence Engine will become the factual foundation of the platform.

Every future AI-generated resume bullet must originate from evidence.

---

## Deliverable

Files:

- engine/evidence_extractor.py
- tests/test_evidence_extractor.py

---

## Inputs

Profile Data

Sections:

- experience
- projects
- certifications
- achievements

---

## Outputs

List[Evidence]

Example:

EXP001
PRJ001
CERT001
ACH001

---

## Success Criteria

- Extract evidence correctly
- Generate unique IDs
- Map source information correctly
- Skip invalid records
- Handle missing sections safely

---

## Tests

- Empty profile
- Missing sections
- Correct ID generation
- Correct field mapping
- Skip empty records
- Handle missing skills

---

## Commit

git commit -m "Add Evidence Extractor"