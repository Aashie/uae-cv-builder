# Skills Section Integration

## Objective

Integrate the deterministic Skills Section Generator into the resume analysis pipeline.

Sprint 22 connects the standalone generator from Sprint 21 into:

```text
Resume Analysis Orchestrator
→ Resume Output Assembler
→ final_resume["skills"]
```

The final resume should use the structured skills schema.

No AI is added in this sprint.

---

## Deliverable

Modify only:

- engine/resume_analysis_orchestrator.py
- tests/test_resume_analysis_orchestrator.py
- engine/resume_output_assembler.py
- tests/test_resume_output_assembler.py

Do not modify:

- engine/skills_section_generator.py
- tests/test_skills_section_generator.py
- data/reference/skills.json
- data/reference/soft_skills.json
- utils/reference_loader.py
- any AI module
- any JSON file
- any UI/API file

---

## Locked Decisions

```text
Q1 = A  Orchestrator calls Skills Section Generator.
Q2 = A  Resume Output Assembler accepts optional skills_section_output.
Q3 = A  Assembler remains backward compatible.
Q4 = B  If Skills Section Generator fails, mark partial and fallback.
Q5 = A  Final resume uses new structured skills schema.
Q6 = A  Old assembler skill fallback remains.
Q7 = A  Modify orchestrator + assembler + their tests.
Q8 = A  Do not modify Skills Section Generator.
```

---

## Public Function Updates

### Resume Analysis Orchestrator

Keep unchanged:

```python
run_resume_analysis(profile: dict, job_description) -> dict
```

### Resume Output Assembler

Update from:

```python
assemble_resume_output(
    resume_draft,
    professional_summary_output,
    experience_bullet_output
)
```

To backward-compatible optional parameter:

```python
assemble_resume_output(
    resume_draft,
    professional_summary_output,
    experience_bullet_output,
    skills_section_output=None
)
```

Old three-argument calls must still work.

---

## Skills Section Generator Call

The orchestrator must call:

```python
generate_skills_section(
    resume_draft,
    matcher_output,
    career_insights
)
```

Call it after these outputs exist:

```text
matcher_output
career_insights
resume_draft
```

Recommended pipeline position:

```text
Evidence Extractor
→ Career Insights Engine
→ Matcher
→ Scorer
→ Skill Gap Analyzer
→ Recommendation Engine
→ Prompt Builder
→ Resume Draft Builder
→ Skills Section Generator
→ Professional Summary Generator
→ AI Response Validator
→ Experience Bullet Generator
→ AI Response Validator
→ Hallucination Checker
→ Resume Output Assembler
```

---

## Orchestrator Output Additions

Add top-level field:

```python
"skills_section_output": {}
```

The orchestrator final output should include:

```python
"skills_section_output": skills_section_output
```

Existing fields must remain stable.

---

## Resume Output Assembler Behavior

Assembler should use `skills_section_output` first when available and successful.

Expected skills output:

```python
{
    "technical": [],
    "soft": [],
    "tools": [],
    "domain": [],
    "matched_skills": [],
    "strongest_skills": []
}
```

Final resume should contain:

```python
final_resume["skills"] = {
    "technical": [],
    "soft": [],
    "tools": [],
    "domain": [],
    "matched_skills": [],
    "strongest_skills": []
}
```

---

## Backward Compatibility Rule

Old calls must still work:

```python
assemble_resume_output(
    resume_draft,
    professional_summary_output,
    experience_bullet_output
)
```

When `skills_section_output` is missing, None, failed, or invalid, assembler falls back safely.

Fallback shape:

```python
{
    "technical": resume_draft.get("key_skills", []),
    "soft": [],
    "tools": [],
    "domain": [],
    "matched_skills": resume_draft.get("matched_skills", []),
    "strongest_skills": []
}
```

---

## Skills Section Failure Rule

If Skills Section Generator returns:

```python
{"status": "failed", ...}
```

or raises unexpectedly:

```text
Do not fail the entire pipeline.
Mark orchestrator partial.
Add an error.
Continue with assembler fallback skills.
```

Recommended error:

```text
Skills section generation failed.
```

If generator returns partial:

```text
Mark orchestrator partial.
Keep generated skills_section.
Pass it to assembler.
Include recoverable errors if useful.
```

Recommended error:

```text
Skills section generation returned partial status.
```

---

## Assembler Skills Source Metadata

Update assembler metadata with:

```python
"skills_source": "skills_section_generator" | "resume_draft_fallback"
```

Rules:

```text
skills_section_generator → valid skills_section_output was used
resume_draft_fallback    → fallback skills from resume_draft were used
```

Existing metadata fields must remain:

```python
assembled_by
version
summary_source
bullet_source
```

---

## No AI Rule

Sprint 22 must not add:

- Gemini
- OpenAI
- LLM calls
- prompt generation
- web search
- Search Grounding
- AI categorization

---

## No Generator Modification Rule

Sprint 22 treats Sprint 21 as stable.

Do not modify:

```text
engine/skills_section_generator.py
tests/test_skills_section_generator.py
```

---

## Tests

Required assembler tests:

- old 3-argument assembler call still works
- assembler accepts optional skills_section_output
- assembler uses skills_section_output when status is success
- assembler uses skills_section_output when status is partial but skills_section exists
- assembler falls back when skills_section_output is None
- assembler falls back when skills_section_output is failed
- assembler falls back when skills_section_output is missing skills_section
- final_resume["skills"] uses structured schema
- metadata includes skills_source
- skills_source is skills_section_generator when generator output used
- skills_source is resume_draft_fallback when fallback used
- old resume_draft key_skills/matched_skills fallback remains stable

Required orchestrator tests:

- orchestrator calls generate_skills_section
- orchestrator includes skills_section_output
- orchestrator passes skills_section_output to assembler
- successful pipeline includes structured final_resume["skills"]
- skills section failed status marks orchestrator partial
- skills section partial status marks orchestrator partial
- skills generator exception marks orchestrator partial
- skills generator failure does not stop summary generation
- skills generator failure does not stop bullet generation
- skills generator failure does not stop assembler
- existing hard stops remain unchanged
- no orchestrator integration modifies Skills Section Generator
- no Search Grounding or AI added

---

## Success Criteria

Sprint 22 is complete when:

- Orchestrator calls Skills Section Generator
- Orchestrator output includes skills_section_output
- Resume Output Assembler accepts optional skills_section_output
- Old assembler calls still work
- final_resume["skills"] uses structured schema
- Skills generator failure causes partial status, not failed pipeline
- Fallback skills still work
- Skills Section Generator itself is not modified
- All focused tests pass
- Full suite passes

---

## Commit

```bash
git commit -m "Integrate Skills Section Generator"
```