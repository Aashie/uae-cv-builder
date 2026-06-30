"""
Test Prompt Builder

Purpose:
Unit tests for prompt package aggregation.
"""

from engine.prompt_builder import build_prompt_package
from models.job_description import JobDescription


def make_job(job_title: str = "Data Analyst") -> JobDescription:
    """Create a minimal job description for prompt builder tests."""
    return JobDescription(
        job_title=job_title,
        required_skills=[],
        soft_skills=[],
        experience_level="Mid",
        education="Bachelor's",
    )


def test_complete_inputs() -> None:
    result = build_prompt_package(
        make_job("Operations Coordinator"),
        {"matched_skills": ["Excel"]},
        {"match_score": 85},
        {"critical_gaps": ["Reporting"]},
        {
            "resume_recommendations": ["Highlight Excel experience."],
            "career_recommendations": ["Develop Reporting skills."],
        },
        {"strongest_skills": ["Communication"]},
    )

    assert result == {
        "job_title": "Operations Coordinator",
        "match_score": 85,
        "strongest_skills": ["Communication"],
        "matched_skills": ["Excel"],
        "critical_gaps": ["Reporting"],
        "resume_recommendations": ["Highlight Excel experience."],
        "career_recommendations": ["Develop Reporting skills."],
    }


def test_empty_inputs() -> None:
    result = build_prompt_package(make_job(""), {}, {}, {}, {}, {})

    assert result == {
        "job_title": "",
        "match_score": 0,
        "strongest_skills": [],
        "matched_skills": [],
        "critical_gaps": [],
        "resume_recommendations": [],
        "career_recommendations": [],
    }


def test_missing_keys() -> None:
    result = build_prompt_package(
        make_job("Analyst"),
        {"missing_skills": ["SQL"]},
        {"matched_skill_count": 1},
        {"minor_gaps": []},
        {"readiness_tier": "Ready to Apply"},
        {"skill_frequency": {}},
    )

    assert result["match_score"] == 0
    assert result["strongest_skills"] == []
    assert result["matched_skills"] == []
    assert result["critical_gaps"] == []
    assert result["resume_recommendations"] == []
    assert result["career_recommendations"] == []


def test_correct_job_title_mapping() -> None:
    result = build_prompt_package(make_job("Project Manager"), {}, {}, {}, {}, {})

    assert result["job_title"] == "Project Manager"


def test_correct_match_score_mapping() -> None:
    result = build_prompt_package(make_job(), {}, {"match_score": 92.5}, {}, {}, {})

    assert result["match_score"] == 92.5


def test_correct_strongest_skills_mapping() -> None:
    result = build_prompt_package(
        make_job(),
        {},
        {},
        {},
        {},
        {"strongest_skills": ["Excel", "Reporting"]},
    )

    assert result["strongest_skills"] == ["Excel", "Reporting"]


def test_correct_matched_skills_mapping() -> None:
    result = build_prompt_package(
        make_job(),
        {"matched_skills": ["Excel", "Communication"]},
        {},
        {},
        {},
        {},
    )

    assert result["matched_skills"] == ["Excel", "Communication"]


def test_correct_critical_gaps_mapping() -> None:
    result = build_prompt_package(
        make_job(),
        {},
        {},
        {"critical_gaps": ["Scheduling"]},
        {},
        {},
    )

    assert result["critical_gaps"] == ["Scheduling"]


def test_correct_recommendation_mapping() -> None:
    result = build_prompt_package(
        make_job(),
        {},
        {},
        {},
        {
            "resume_recommendations": ["Highlight Excel experience."],
            "career_recommendations": ["Develop Scheduling skills."],
        },
        {},
    )

    assert result["resume_recommendations"] == ["Highlight Excel experience."]
    assert result["career_recommendations"] == ["Develop Scheduling skills."]
