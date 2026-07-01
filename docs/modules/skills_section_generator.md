# Skills Section Generator

## Objective

Build a deterministic Skills Section Generator.

The generator creates a structured resume skills section from existing project data.

It must not use AI.

It must not invent missing skills.

It must not add skills from the job description unless they are already matched or evidenced.

The generator organizes known skills into clean resume-ready categories.

---

## Deliverable

Files:

- engine/skills_section_generator.py
- tests/test_skills_section_generator.py

No orchestrator integration in Sprint 21.

Orchestrator integration is deferred to Sprint 22.

---

## Locked Decisions

```text
Q1 = A  Deterministic only. No Gemini.
Q2 = A  Use resume_draft + matcher_output + career_insights.
Q3 = A  Do not invent missing job skills.
Q4 = A  Return wrapper with status/errors/skills_section.
Q5 = B  Light deterministic categorization.
Q6 = A  Hard stop if no skills are found from any source.
Q7 = A  Case-insensitive deduplication, preserve readable title case.
Q8 = B  Standalone only. Orchestrator integration in Sprint 22.
```

---

## Public Function

```python
generate_skills_section(
    resume_draft: dict,
    matcher_output: dict,
    career_insights: dict
) -> dict
```

---

## Input Sources

The generator uses only these fields:

```python
resume_draft["key_skills"]
resume_draft["matched_skills"]
matcher_output["matched_skills"]
career_insights["strongest_skills"]
```

Expected input shapes:

```python
resume_draft = {
    "key_skills": [],
    "matched_skills": []
}
```

```python
matcher_output = {
    "matched_skills": []
}
```

```python
career_insights = {
    "strongest_skills": []
}
```

The exact `career_insights["strongest_skills"]` key must be verified against `engine/career_insights_engine.py` during Codex architecture review.

---

## Output Wrapper Schema

```python
{
    "status": "success",
    "errors": [],
    "skills_section": {
        "technical": [],
        "soft": [],
        "tools": [],
        "domain": [],
        "matched_skills": [],
        "strongest_skills": []
    }
}
```

---

## Skills Section Schema

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

Meaning:

```text
technical        Resume-rendered technical skills
soft             Resume-rendered soft skills
tools            Resume-rendered tools/platforms/software
domain           Resume-rendered domain or uncategorized professional skills
matched_skills   ATS/job-match signal metadata
strongest_skills Career strength signal metadata
```

Important:

`matched_skills` and `strongest_skills` are retained as separate metadata fields alongside categorized skills.

They are not removed from category lists.

They serve different downstream purposes:

```text
technical/soft/tools/domain  → resume skills rendering
matched_skills               → ATS/job-match coverage signal
strongest_skills             → summary/headline emphasis signal
```

Each individual list should be deduplicated case-insensitively.

---

## Skill Collection Rule

Collect skills from:

```python
resume_draft.get("key_skills", [])
resume_draft.get("matched_skills", [])
matcher_output.get("matched_skills", [])
career_insights.get("strongest_skills", [])
```

Ignore:

- None
- empty strings
- non-string values
- whitespace-only strings

Do not collect:

- missing job skills
- raw job description skills
- AI-generated skill guesses
- skills from external web/search grounding
- skills from unsupported input fields

---

## Closed Universe Rule

The generator must not invent skills.

Allowed:

```text
Copy existing skills from approved inputs.
Categorize existing skills.
Deduplicate existing skills.
Normalize spacing and readable casing.
```

Forbidden:

```text
Add missing job skills.
Infer skills from job title.
Infer skills from experience text.
Use web/search grounding.
Ask Gemini.
Generate new skills.
```

---

## Deduplication Rule

Deduplicate case-insensitively.

Examples:

```text
"python", "Python", "PYTHON" → "Python"
"project management", "Project Management" → "Project Management"
```

Preserve readable title case in output.

Recommended normalization:

```text
strip whitespace
collapse repeated spaces
convert to title case unless acronym is known
```

Known acronym preservation may include:

```text
AI
AWS
CRM
CSS
GIS
HTML
IELTS
IT
JSON
LLM
MS
PDF
SDLC
SEO
SQL
UAE
UI
UAT
UX
WAN
LAN
```

---

## Categorization Rule

Use deterministic categorization only.

Reference data:

```text
data/reference/skills.json       → technical reference
data/reference/soft_skills.json  → soft skills reference
```

Use existing reference loading utilities if available.

Do not modify existing reference JSON files.

Do not create new reference JSON files in Sprint 21.

---

## Categorization Priority

For each skill, apply this order:

```text
1. If skill exists in technical reference data → technical
2. If skill exists in soft skills reference data → soft
3. If skill matches inline tools keyword list → tools
4. Otherwise → domain
```

Matching should be case-insensitive.

---

## Inline Tools Keyword List

Sprint 21 uses an inline constant for tools/platforms/software.

Example tools keywords:

```python
TOOLS_KEYWORDS = {
    "excel",
    "microsoft excel",
    "word",
    "microsoft word",
    "powerpoint",
    "microsoft powerpoint",
    "outlook",
    "crm",
    "salesforce",
    "hubspot",
    "wordpress",
    "canva",
    "capcut",
    "google analytics",
    "meta ads",
    "jira",
    "trello",
    "asana",
    "notion",
    "slack",
    "selenium",
    "jupyter",
    "mysql",
    "linux",
    "ubuntu",
    "aws",
    "arcgis",
    "qgis",
    "autocad"
}
```

This list is allowed in code for V1.

A dedicated `tools.json` reference database may be added later in V2.

---

## Reference Loading Failure

If reference data cannot be loaded:

```text
Do not crash.
Use empty reference lists.
Add an error message.
Continue categorization.
Unknown skills fall into domain unless they match tools keywords.
Return partial status.
```

Recommended errors:

```text
Technical skills reference data could not be loaded.
Soft skills reference data could not be loaded.
```

---

## Status Values

### success

Returned when:

- at least one skill is found
- reference data loads successfully
- categorization completes without recoverable errors

```python
status = "success"
errors = []
```

---

### partial

Returned when:

- at least one skill is found
- skills section can still be generated
- one or more recoverable issues occurred

Examples:

```text
technical reference data failed to load
soft skills reference data failed to load
one input section is missing
non-string skill values were ignored
```

```python
status = "partial"
errors != []
```

---

### failed

Returned when no usable skills are found from any approved source.

```python
{
    "status": "failed",
    "errors": ["No skills found. Cannot generate skills section."],
    "skills_section": {
        "technical": [],
        "soft": [],
        "tools": [],
        "domain": [],
        "matched_skills": [],
        "strongest_skills": []
    }
}
```

---

## Hard Stop Conditions

Hard stop when:

```text
No usable skills exist from any approved source.
```

This includes:

```text
resume_draft is None or empty
matcher_output is None or empty
career_insights is None or empty
all skill lists missing or empty
all skill values invalid
```

Error:

```text
No skills found. Cannot generate skills section.
```

---

## Metadata Lists

### matched_skills

Build from:

```python
resume_draft["matched_skills"]
matcher_output["matched_skills"]
```

Deduplicate case-insensitively.

Do not remove these skills from categorized lists.

---

### strongest_skills

Build from:

```python
career_insights["strongest_skills"]
```

Deduplicate case-insensitively.

Do not remove these skills from categorized lists.

---

## Missing Input Behavior

If an input dict is missing or None:

```text
Continue with empty data from that source.
Mark partial only if useful.
```

Examples:

```text
resume_draft missing → continue using matcher_output and career_insights if available
matcher_output missing → continue using resume_draft and career_insights if available
career_insights missing → continue using resume_draft and matcher_output if available
```

But if all sources are empty:

```text
Return failed.
```

---

## No AI Rule

Sprint 21 must not use:

- Gemini
- OpenAI
- LLM calls
- prompt builder
- web search
- search grounding
- AI categorization

---

## No Orchestrator Integration

Sprint 21 does not modify:

- engine/resume_analysis_orchestrator.py
- tests/test_resume_analysis_orchestrator.py

Integration happens in Sprint 22.

---

## Not Included In Sprint 21

Sprint 21 does not include:

- real Gemini integration
- AI-generated skills
- job description missing-skill injection
- resume output assembler integration
- orchestrator integration
- Streamlit UI
- export engine
- tools.json reference file
- advanced skill weighting
- proficiency scoring
- years-of-experience scoring per skill

---

## Tests

Required tests:

- successful skills section generation
- output wrapper contains status, errors, skills_section
- skills_section contains technical, soft, tools, domain
- skills_section contains matched_skills
- skills_section contains strongest_skills
- collects skills from resume_draft key_skills
- collects skills from resume_draft matched_skills
- collects skills from matcher_output matched_skills
- collects skills from career_insights strongest_skills
- verifies career_insights strongest_skills key
- does not invent missing job skills
- ignores unsupported input fields
- ignores None values
- ignores empty strings
- ignores non-string values
- deduplicates skills case-insensitively
- preserves readable title case
- categorizes technical skills from skills reference data
- categorizes soft skills from soft skills reference data
- categorizes tools using inline tools keyword list
- categorizes unknown skills as domain
- matched_skills retained separately from categories
- strongest_skills retained separately from categories
- matched_skills are not removed from categorized skills
- strongest_skills are not removed from categorized skills
- no skills found returns failed status
- None inputs return failed if no skills found
- missing one input can still succeed if other sources contain skills
- reference loading failure returns partial status
- reference loading failure falls back safely
- no Gemini/API call required
- no orchestrator modification
- stable output schema

---

## Success Criteria

Sprint 21 is complete when:

- Skills Section Generator exists
- It is deterministic only
- It uses only approved input sources
- It does not invent skills
- It deduplicates skills case-insensitively
- It categorizes skills into technical, soft, tools, and domain
- It preserves matched_skills separately
- It preserves strongest_skills separately
- It hard-stops when no skills exist
- It handles missing inputs safely
- It handles reference loading failure safely
- It does not modify orchestrator
- All Sprint 21 tests pass
- Full test suite passes

---

## Commit

```bash
git commit -m "Add Skills Section Generator"
```
