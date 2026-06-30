"""
Test Matcher

Purpose:
Unit tests for the skill matcher module.
"""

from engine.matcher import match_job_to_profile
from models.evidence import Evidence
from models.job_description import JobDescription


def make_job(required_skills: list[str]) -> JobDescription:
    """Create a minimal job description for matcher tests."""
    return JobDescription(
        job_title="Software Engineer",
        required_skills=required_skills,
        soft_skills=[],
        experience_level="Mid",
        education="Bachelor's",
    )


def make_evidence(evidence_id: str, skills: list[str]) -> Evidence:
    """Create a minimal evidence item for matcher tests."""
    return Evidence(
        id=evidence_id,
        source_type="profile",
        source_id="profile-1",
        category="experience",
        text="Candidate evidence",
        skills=skills,
    )


def test_matching_profile_skills_only() -> None:
    result = match_job_to_profile(
        make_job(["Python", "SQL"]),
        ["python", "sql"],
        [],
    )

    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == []
    assert result["evidence_matches"] == {}
    assert result["score"] == 100


def test_matching_evidence_skills_only() -> None:
    result = match_job_to_profile(
        make_job(["Python", "SQL"]),
        [],
        [make_evidence("ev-1", ["python"]), make_evidence("ev-2", ["SQL"])],
    )

    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == []
    assert result["evidence_matches"] == {
        "Python": ["ev-1"],
        "SQL": ["ev-2"],
    }
    assert result["score"] == 100


def test_matching_both_profile_and_evidence_skills() -> None:
    result = match_job_to_profile(
        make_job(["Python", "SQL", "Docker"]),
        ["python"],
        [make_evidence("ev-1", ["SQL"]), make_evidence("ev-2", ["docker"])],
    )

    assert result["matched_skills"] == ["Python", "SQL", "Docker"]
    assert result["missing_skills"] == []
    assert result["evidence_matches"] == {
        "SQL": ["ev-1"],
        "Docker": ["ev-2"],
    }
    assert result["score"] == 100


def test_missing_skills() -> None:
    result = match_job_to_profile(
        make_job(["Python", "SQL", "Docker"]),
        ["python"],
        [],
    )

    assert result["matched_skills"] == ["Python"]
    assert result["missing_skills"] == ["SQL", "Docker"]
    assert result["evidence_matches"] == {}


def test_score_calculation() -> None:
    result = match_job_to_profile(
        make_job(["Python", "SQL", "Docker", "AWS"]),
        ["python", "aws"],
        [],
    )

    assert result["score"] == 50


def test_empty_required_skills() -> None:
    result = match_job_to_profile(make_job([]), ["python"], [make_evidence("ev-1", ["SQL"])])

    assert result == {
        "matched_skills": [],
        "missing_skills": [],
        "evidence_matches": {},
        "score": 0,
    }


def test_empty_profile_and_evidence() -> None:
    result = match_job_to_profile(make_job(["Python", "SQL"]), [], [])

    assert result["matched_skills"] == []
    assert result["missing_skills"] == ["Python", "SQL"]
    assert result["evidence_matches"] == {}
    assert result["score"] == 0


def test_duplicate_required_and_evidence_skills_are_removed() -> None:
    result = match_job_to_profile(
        make_job(["Python", "python", " SQL "]),
        ["PYTHON"],
        [make_evidence("ev-1", ["sql", "SQL"]), make_evidence("ev-1", ["SQL"])],
    )

    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == []
    assert result["evidence_matches"] == {"SQL": ["ev-1"]}
    assert result["score"] == 100
