# Agent Workflow

## Project

ATS-UAE-RESUME-BUILDER / UAE Career Intelligence Platform

## Repository

`C:\Users\hp\Desktop\uae-cv-builder`

## Core Rule

NO INVENTION. The system must never invent candidate claims.

## Roles

- ChatGPT = architect, sprint planner, final reviewer
- Work = long-form audit, documentation, PRD, reports, QA checklist assistant
- Codex = implementation worker for code/docs/tests
- Gemini/Kimi = optional reviewer for risky sprints
- User = final approver, manual tester, commit decision maker

## Risk Levels

Low-risk:

- docs
- UI wording
- formatting
- tests that do not change logic

Medium-risk:

- parser display behavior
- export formatting
- recommendation wording
- UI gates

High-risk:

- candidate parser
- JD parser
- matcher
- evidence trace
- hallucination checker
- DOCX safety gate
- orchestrator
- anything affecting candidate evidence or no-invention safety

## Rules

- High-risk sprints require review before implementation.
- Codex must obey allowed/forbidden files.
- Codex must not commit/push unless explicitly told.
- Work should not edit code.
- Only one agent edits the repo at a time.
- User approves final commit.
