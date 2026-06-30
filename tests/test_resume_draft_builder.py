"""
Test Resume Draft Builder

Purpose:
Unit tests for deterministic resume draft generation.
"""

from engine.resume_draft_builder import build_resume_draft


def test_complete_input() -> None:
    result = build_resume_draft(
        {
            "job_title": "Data Analyst",
            "match_score": 87,
            "strongest_skills": ["Excel", "Reporting"],
            "matched_skills": ["Excel"],
            "resume_recommendations": ["Highlight Excel experience."],
        }
    )

    assert result == {
        "job_title": "Data Analyst",
        "professional_summary": (
            "Professional with a 87% match score for Data Analyst opportunities."
        ),
        "key_skills": ["Excel", "Reporting"],
        "matched_skills": ["Excel"],
        "resume_bullets": ["Highlight Excel experience."],
    }


def test_empty_input() -> None:
    result = build_resume_draft({})

    assert result == {
        "job_title": "",
        "professional_summary": "Professional with a 0% match score for  opportunities.",
        "key_skills": [],
        "matched_skills": [],
        "resume_bullets": [],
    }


def test_missing_keys() -> None:
    result = build_resume_draft({"job_title": "Coordinator"})

    assert result == {
        "job_title": "Coordinator",
        "professional_summary": (
            "Professional with a 0% match score for Coordinator opportunities."
        ),
        "key_skills": [],
        "matched_skills": [],
        "resume_bullets": [],
    }


def test_summary_generation() -> None:
    result = build_resume_draft({"job_title": "Project Manager", "match_score": 92.5})

    assert result["professional_summary"] == (
        "Professional with a 92.5% match score for Project Manager opportunities."
    )


def test_key_skills_mapping() -> None:
    result = build_resume_draft({"strongest_skills": ["Communication", "Excel"]})

    assert result["key_skills"] == ["Communication", "Excel"]


def test_matched_skills_mapping() -> None:
    result = build_resume_draft({"matched_skills": ["Python", "SQL"]})

    assert result["matched_skills"] == ["Python", "SQL"]


def test_resume_bullet_mapping() -> None:
    result = build_resume_draft(
        {"resume_recommendations": ["Highlight Scheduling experience."]}
    )

    assert result["resume_bullets"] == ["Highlight Scheduling experience."]
