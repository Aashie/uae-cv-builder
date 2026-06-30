"""
Test Scorer

Purpose:
Unit tests for the skill-only scoring engine.
"""

from engine.scorer import calculate_match_score
from models.job_description import JobDescription


def make_job(required_skills: list[str]) -> JobDescription:
    """Create a minimal job description for scorer tests."""
    return JobDescription(
        job_title="Software Engineer",
        required_skills=required_skills,
        soft_skills=[],
        experience_level="Mid",
        education="Bachelor's",
    )


def test_perfect_match_returns_100() -> None:
    result = calculate_match_score(
        {"matched_skills": ["Python", "SQL"], "missing_skills": [], "evidence_matches": {}},
        make_job(["Python", "SQL"]),
    )

    assert result["match_score"] == 100


def test_partial_match_returns_correct_percentage() -> None:
    result = calculate_match_score(
        {
            "matched_skills": ["Python", "SQL"],
            "missing_skills": ["Docker", "AWS"],
            "evidence_matches": {},
        },
        make_job(["Python", "SQL", "Docker", "AWS"]),
    )

    assert result["match_score"] == 50


def test_no_match_returns_0() -> None:
    result = calculate_match_score(
        {
            "matched_skills": [],
            "missing_skills": ["Python", "SQL"],
            "evidence_matches": {},
        },
        make_job(["Python", "SQL"]),
    )

    assert result["match_score"] == 0


def test_empty_required_skills_returns_0() -> None:
    result = calculate_match_score(
        {"matched_skills": ["Python"], "missing_skills": [], "evidence_matches": {}},
        make_job([]),
    )

    assert result["match_score"] == 0
    assert result["required_skill_count"] == 0


def test_empty_matcher_output_returns_0() -> None:
    result = calculate_match_score({}, make_job(["Python", "SQL"]))

    assert result["match_score"] == 0
    assert result["matched_skill_count"] == 0
    assert result["required_skill_count"] == 2


def test_score_is_rounded_to_2_decimals() -> None:
    result = calculate_match_score(
        {"matched_skills": ["Python"], "missing_skills": ["SQL", "Docker"], "evidence_matches": {}},
        make_job(["Python", "SQL", "Docker"]),
    )

    assert result["match_score"] == 33.33


def test_matched_skill_count_is_correct() -> None:
    result = calculate_match_score(
        {"matched_skills": ["Python", "SQL", "AWS"], "missing_skills": [], "evidence_matches": {}},
        make_job(["Python", "SQL", "AWS"]),
    )

    assert result["matched_skill_count"] == 3


def test_required_skill_count_is_correct() -> None:
    result = calculate_match_score(
        {"matched_skills": ["Python"], "missing_skills": ["SQL"], "evidence_matches": {}},
        make_job(["Python", "SQL"]),
    )

    assert result["required_skill_count"] == 2
