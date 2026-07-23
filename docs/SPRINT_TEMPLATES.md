# Sprint Templates

## 1. Gemini/Kimi Review Prompt Template

```markdown
You are reviewing Sprint [SPRINT NUMBER]: [SPRINT TITLE].

Project context:
[PROJECT CONTEXT]

Current status:
[CURRENT STATUS]

Problem:
[PROBLEM]

Proposed goal:
[PROPOSED GOAL]

Allowed files:
[ALLOWED FILES]

Forbidden files:
[FORBIDDEN FILES]

No-invention constraints:
- Candidate claims must come only from candidate evidence or reviewed profile text.
- JD-only requirements must remain gaps/recommendations and must not be inserted into candidate profile or resume.
- If uncertain, preserve or block; never invent.

Test expectations:
[TEST EXPECTATIONS]

Review questions:
1. Is the sprint scope narrow enough?
2. Are allowed and forbidden files correct?
3. Could the change invent candidate claims?
4. Could this weaken validation, evidence trace, or DOCX safety gates?
5. Are the tests sufficient and focused?

Verdict format:
1. Verdict: approve / approve with changes / reject
2. Required changes
3. Risks
4. Test recommendations
5. Notes for Codex implementation
```

## 2. Read-Only Audit Sprint Prompt Template

```markdown
You are working in this repository:
C:\Users\hp\Desktop\uae-cv-builder

SPRINT [SPRINT NUMBER]:
[SPRINT TITLE]

ROLE:
You are my QA/debugging assistant.

This is NOT an implementation sprint.
Do not edit files.
Do not fix anything.
Do not create files.
Do not create tests.
Do not refactor.
Do not commit.
Do not push.

Commands to run:
1. git status --short
2. [FOCUSED OR FULL TEST COMMANDS]

Files allowed for inspection:
[FILES / DIRECTORIES]

Questions to answer:
[QUESTIONS]

Output control:
- Do not dump full modules.
- Use short targeted excerpts only if necessary.
- Report findings, not patches.

Report format:
1. Initial git status
2. Commands run
3. Test results
4. Files inspected
5. Findings
6. Root cause, if identifiable
7. Recommended next sprint
8. Confirmation no files edited/created
9. Final git status

Final command:
git status --short

No commit/push.
```

## 3. Implementation Sprint Prompt Template

```markdown
You are working in this repository:
C:\Users\hp\Desktop\uae-cv-builder

SPRINT [SPRINT NUMBER]:
[SPRINT TITLE]

ROLE:
You are my implementation worker.

Exact goal:
[EXACT GOAL]

Allowed files:
[ALLOWED FILES]

Forbidden files:
[FORBIDDEN FILES]

Required behavior:
[REQUIRED BEHAVIOR]

Safety rules:
- Do not invent candidate claims.
- Do not add JD-only skills to candidate profile or resume.
- Do not broaden scope beyond the allowed files.
- Preserve existing behavior unless this sprint explicitly changes it.
- Do not commit, push, or tag.

Test commands:
1. [FOCUSED TEST COMMAND]
2. .\venv\Scripts\python.exe -m pytest -q

Manual QA expectations:
[MANUAL QA EXPECTATIONS OR "Not required"]

Report format:
1. Changed files
2. Exact functions changed
3. Tests added/updated
4. Behavior added/changed
5. Focused test command run
6. Focused test result
7. Full test command run
8. Full test result
9. Manual QA result, if performed
10. Blockers
11. Confirmation no forbidden files changed
12. Confirmation no commit/push/tag performed
```

## 4. Verification Checklist Template

```markdown
Verification checklist:
1. Initial git status:
   git status --short
2. Review diff:
   git diff -- [EXPECTED FILES]
3. Focused tests:
   [FOCUSED TEST COMMAND]
4. Full tests:
   .\venv\Scripts\python.exe -m pytest -q
5. Manual QA:
   [MANUAL STEPS]
6. Final git status:
   git status --short

Expected outputs:
- Only expected files changed.
- Focused tests pass.
- Full suite passes.
- Manual QA result recorded, if performed.
- No commit/push/tag unless explicitly requested.
```

## 5. Commit/Push Checklist Template

```markdown
Commit/push checklist:
1. Confirm approved scope and test results.
2. Stage exact files only:
   git add [EXACT FILES]
3. Commit:
   git commit -m "[COMMIT MESSAGE]"
4. Push:
   git push origin main
5. Confirm status:
   git status --short
6. Confirm latest log:
   git log --oneline -5
```

## 6. Manual QA Checklist Template

```markdown
Manual QA checklist:
1. Input files used:
   - CV:
   - JD:
2. Parsed candidate profile:
   - Name:
   - Skills:
   - Experience:
   - Certifications:
   - Warnings/errors:
3. Parsed JD:
   - Job title:
   - Required skills:
   - Experience level:
   - Education:
   - Warnings/errors:
4. Analysis status:
   - Internal status:
   - Completed stages:
   - Errors/warnings:
5. Matched/missing skills:
   - Matched:
   - Missing:
6. Skill gaps:
   - Critical:
   - Minor:
7. Recommendations:
   - Resume:
   - Career:
   - Awkward/non-skill lines:
8. Resume preview:
   - Professional summary:
   - Skills:
   - Experience highlights:
   - Empty/weak sections:
9. Evidence trace:
   - Shown:
   - Errors/warnings:
10. DOCX gate:
   - Allowed/blocked:
   - Blockers:
11. No-invention check:
   - JD-only skills inserted?
   - Unsupported claims?
   - Fake degree/certification/tool/achievement?
```

## 7. Codex Report Format Template

```markdown
1. Changed files
2. Functions changed
3. Tests added/updated
4. Commands run
5. Test results
6. Manual QA result, if performed
7. Blockers
8. Confirmation no forbidden files changed
9. Confirmation no source/test/app behavior changes outside scope
10. Confirmation no commit/push/tag performed
```
