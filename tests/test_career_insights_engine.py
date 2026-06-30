"""
Test Career Insights Engine

Purpose:
Unit tests for evidence-based career insight analysis.
"""

from engine.career_insights_engine import analyze_career_insights
from models.evidence import Evidence


def make_evidence(evidence_id: str, skills: list[str]) -> Evidence:
    """Create a minimal evidence item for career insights tests."""
    return Evidence(
        id=evidence_id,
        source_type="profile",
        source_id="profile-1",
        category="experience",
        text="Candidate evidence",
        skills=skills,
    )


def test_empty_evidence_returns_empty_output() -> None:
    result = analyze_career_insights([])

    assert result == {
        "strongest_skills": [],
        "skill_frequency": {},
        "total_evidence_items": 0,
        "total_unique_skills": 0,
    }


def test_single_evidence_item_counts_skills() -> None:
    result = analyze_career_insights([make_evidence("ev-1", ["python", "sql"])])

    assert result["skill_frequency"] == {"Python": 1, "Sql": 1}
    assert result["strongest_skills"] == ["Python", "Sql"]


def test_multiple_evidence_items_count_repeated_skills() -> None:
    result = analyze_career_insights(
        [
            make_evidence("ev-1", ["Python", "SQL"]),
            make_evidence("ev-2", ["Python", "Excel"]),
        ]
    )

    assert result["skill_frequency"] == {"Python": 2, "Sql": 1, "Excel": 1}


def test_case_insensitive_skill_counting() -> None:
    result = analyze_career_insights(
        [
            make_evidence("ev-1", ["python"]),
            make_evidence("ev-2", ["PYTHON"]),
            make_evidence("ev-3", ["Python"]),
        ]
    )

    assert result["skill_frequency"] == {"Python": 3}


def test_strongest_skills_sorted_by_frequency_descending() -> None:
    result = analyze_career_insights(
        [
            make_evidence("ev-1", ["Excel", "Python"]),
            make_evidence("ev-2", ["Python"]),
            make_evidence("ev-3", ["Python", "Reporting"]),
        ]
    )

    assert result["strongest_skills"] == ["Python", "Excel", "Reporting"]


def test_tied_skills_sorted_alphabetically() -> None:
    result = analyze_career_insights(
        [
            make_evidence("ev-1", ["Scheduling"]),
            make_evidence("ev-2", ["Reporting"]),
            make_evidence("ev-3", ["Excel"]),
        ]
    )

    assert result["strongest_skills"] == ["Excel", "Reporting", "Scheduling"]


def test_total_evidence_items_is_correct() -> None:
    result = analyze_career_insights(
        [
            make_evidence("ev-1", ["Python"]),
            make_evidence("ev-2", []),
            make_evidence("ev-3", ["Excel"]),
        ]
    )

    assert result["total_evidence_items"] == 3


def test_total_unique_skills_is_correct() -> None:
    result = analyze_career_insights(
        [
            make_evidence("ev-1", ["Python", "SQL"]),
            make_evidence("ev-2", ["python", "Excel"]),
        ]
    )

    assert result["total_unique_skills"] == 3


def test_evidence_items_with_no_skills_are_handled_safely() -> None:
    result = analyze_career_insights(
        [
            make_evidence("ev-1", []),
            make_evidence("ev-2", ["Python"]),
        ]
    )

    assert result["skill_frequency"] == {"Python": 1}
    assert result["total_evidence_items"] == 2
