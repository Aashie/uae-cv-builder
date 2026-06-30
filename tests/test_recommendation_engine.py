"""
Test Recommendation Engine

Purpose:
Unit tests for deterministic recommendation generation.
"""

from engine.recommendation_engine import generate_recommendations


def test_ready_to_apply_tier() -> None:
    result = generate_recommendations({}, {}, {"match_score": 90})

    assert result["readiness_tier"] == "Ready to Apply"


def test_apply_with_minor_gaps_tier() -> None:
    result = generate_recommendations({}, {}, {"match_score": 70})

    assert result["readiness_tier"] == "Apply with Minor Gaps"


def test_targeted_upskilling_recommended_tier() -> None:
    result = generate_recommendations({}, {}, {"match_score": 40})

    assert result["readiness_tier"] == "Targeted Upskilling Recommended"


def test_significant_upskilling_required_tier() -> None:
    result = generate_recommendations({}, {}, {"match_score": 39})

    assert result["readiness_tier"] == "Significant Upskilling Required"


def test_matched_skills_create_resume_recommendations() -> None:
    result = generate_recommendations(
        {"matched_skills": ["Excel", "Communication"]},
        {"critical_gaps": []},
        {"match_score": 95},
    )

    assert result["resume_recommendations"] == [
        "Highlight Excel experience.",
        "Highlight Communication experience.",
    ]


def test_critical_gaps_create_career_recommendations() -> None:
    result = generate_recommendations(
        {"matched_skills": []},
        {"critical_gaps": ["Reporting", "Scheduling"]},
        {"match_score": 30},
    )

    assert result["career_recommendations"] == [
        "Develop Reporting skills.",
        "Develop Scheduling skills.",
    ]


def test_empty_inputs() -> None:
    result = generate_recommendations({}, {}, {})

    assert result == {
        "readiness_tier": "Significant Upskilling Required",
        "resume_recommendations": [],
        "career_recommendations": [],
    }


def test_no_overlap_between_resume_and_career_recommendations() -> None:
    result = generate_recommendations(
        {"matched_skills": ["Excel", "Communication"]},
        {"critical_gaps": ["Excel", "Reporting"]},
        {"match_score": 75},
    )

    assert result["resume_recommendations"] == ["Highlight Communication experience."]
    assert result["career_recommendations"] == ["Develop Reporting skills."]
