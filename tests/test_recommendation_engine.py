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
        (
            "Evidence-supported match: Excel. Consider highlighting this only where "
            "it is supported by your CV."
        ),
        (
            "Evidence-supported match: Communication. Consider highlighting this "
            "only where it is supported by your CV."
        ),
    ]


def test_critical_gaps_create_career_recommendations() -> None:
    result = generate_recommendations(
        {"matched_skills": []},
        {"critical_gaps": ["Reporting", "Scheduling"]},
        {"match_score": 30},
    )

    assert result["career_recommendations"] == [
        (
            "Requirement to address: Reporting. Add this to your resume only if it "
            "is true and supported by your experience; otherwise treat it as a "
            "learning or interview preparation target."
        ),
        (
            "Requirement to address: Scheduling. Add this to your resume only if "
            "it is true and supported by your experience; otherwise treat it as a "
            "learning or interview preparation target."
        ),
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

    assert result["resume_recommendations"] == [
        (
            "Evidence-supported match: Communication. Consider highlighting this "
            "only where it is supported by your CV."
        )
    ]
    assert result["career_recommendations"] == [
        (
            "Requirement to address: Reporting. Add this to your resume only if it "
            "is true and supported by your experience; otherwise treat it as a "
            "learning or interview preparation target."
        )
    ]


def test_matched_english_uses_evidence_supported_wording() -> None:
    result = generate_recommendations(
        {"matched_skills": ["Proficiency in English"]},
        {"critical_gaps": []},
        {"match_score": 90},
    )

    recommendation = result["resume_recommendations"][0]

    assert recommendation == (
        "Evidence-supported match: Proficiency in English. Consider highlighting "
        "this only where it is supported by your CV."
    )
    assert recommendation != "Highlight Proficiency in English experience."
    assert not recommendation.startswith("Highlight ")


def test_matched_ms_office_jd_phrase_is_display_normalized() -> None:
    result = generate_recommendations(
        {"matched_skills": ["Excellent knowledge of MS Office"]},
        {"critical_gaps": []},
        {"match_score": 90},
    )

    recommendation = result["resume_recommendations"][0]

    assert recommendation == (
        "Evidence-supported match: Microsoft Office. Consider highlighting this "
        "only where it is supported by your CV."
    )
    assert "Excellent knowledge" not in recommendation


def test_missing_crm_gap_uses_readable_gap_safe_wording() -> None:
    result = generate_recommendations(
        {"matched_skills": []},
        {"critical_gaps": ["Hands-on experience with CRM software is a plus"]},
        {"match_score": 30},
    )

    assert result["resume_recommendations"] == []
    assert result["career_recommendations"] == [
        (
            "Requirement to address: CRM software. Add this to your resume only if "
            "it is true and supported by your experience; otherwise treat it as a "
            "learning or interview preparation target."
        )
    ]


def test_missing_skills_are_not_candidate_owned_strengths() -> None:
    result = generate_recommendations(
        {"matched_skills": []},
        {"critical_gaps": ["CRM software"]},
        {"match_score": 30},
    )

    recommendation = result["career_recommendations"][0]

    assert recommendation.startswith("Requirement to address: CRM software.")
    assert "Evidence-supported match" not in recommendation
    assert result["resume_recommendations"] == []


def test_old_bad_recommendation_patterns_are_not_generated() -> None:
    result = generate_recommendations(
        {"matched_skills": ["Proficiency in English"]},
        {"critical_gaps": ["Hands-on experience with CRM software is a plus"]},
        {"match_score": 50},
    )
    all_recommendations = (
        result["resume_recommendations"] + result["career_recommendations"]
    )

    assert "Highlight Proficiency in English experience." not in all_recommendations
    assert (
        "Develop Hands-on experience with CRM software is a plus skills."
        not in all_recommendations
    )
