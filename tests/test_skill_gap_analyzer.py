"""
Test Skill Gap Analyzer

Purpose:
Unit tests for V1 skill gap classification.
"""

from engine.skill_gap_analyzer import analyze_skill_gaps


def test_high_readiness() -> None:
    result = analyze_skill_gaps({"missing_skills": [], "score": 80})

    assert result["application_readiness"] == "high"


def test_medium_readiness() -> None:
    result = analyze_skill_gaps({"missing_skills": ["Docker"], "score": 50})

    assert result["application_readiness"] == "medium"


def test_low_readiness() -> None:
    result = analyze_skill_gaps({"missing_skills": ["Docker"], "score": 49.99})

    assert result["application_readiness"] == "low"


def test_empty_matcher_output() -> None:
    result = analyze_skill_gaps({})

    assert result == {
        "critical_gaps": [],
        "minor_gaps": [],
        "application_readiness": "low",
    }


def test_missing_skills_become_critical_gaps() -> None:
    result = analyze_skill_gaps({"missing_skills": ["Python", "SQL"], "score": 25})

    assert result["critical_gaps"] == ["Python", "SQL"]


def test_minor_gaps_is_always_empty_in_v1() -> None:
    result = analyze_skill_gaps({"missing_skills": ["Python"], "score": 10})

    assert result["minor_gaps"] == []


def test_missing_score_defaults_to_low() -> None:
    result = analyze_skill_gaps({"missing_skills": []})

    assert result["application_readiness"] == "low"


def test_missing_missing_skills_defaults_to_empty_critical_gaps() -> None:
    result = analyze_skill_gaps({"score": 100})

    assert result["critical_gaps"] == []
