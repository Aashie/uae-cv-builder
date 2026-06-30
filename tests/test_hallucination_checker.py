"""
Test Hallucination Checker

Purpose:
Unit tests for evidence-linked hallucination checks.
"""

from engine.hallucination_checker import check_hallucinations
from models.evidence import Evidence


def make_evidence(evidence_id: str, text: str) -> Evidence:
    """Create a minimal evidence item for hallucination checker tests."""
    return Evidence(
        id=evidence_id,
        source_type="profile",
        source_id="profile-1",
        category="experience",
        text=text,
        skills=[],
    )


def make_ai_output(bullets: list[dict]) -> dict:
    """Create a minimal AI output fixture."""
    return {"experience_bullets": bullets}


def test_valid_overlap_passes() -> None:
    bullet = {
        "text": "Led communication across multiple teams.",
        "source_evidence_id": "ev-1",
    }

    result = check_hallucinations(
        make_ai_output([bullet]),
        [make_evidence("ev-1", "Coordinated communication with project teams.")],
    )

    assert result["passed_bullets"] == [bullet]
    assert result["failed_bullets"] == []
    assert result["hallucination_count"] == 0


def test_no_overlap_fails() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {
                    "text": "Managed a team of 50 employees.",
                    "source_evidence_id": "ev-1",
                }
            ]
        ),
        [make_evidence("ev-1", "Handled client communications.")],
    )

    assert result["passed_bullets"] == []
    assert result["failed_bullets"] == [
        {
            "bullet": "Managed a team of 50 employees.",
            "reason": "No keyword overlap with linked evidence.",
        }
    ]
    assert result["hallucination_count"] == 1


def test_missing_evidence_id_fails() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {
                    "text": "Improved reporting workflows.",
                    "source_evidence_id": "missing",
                }
            ]
        ),
        [make_evidence("ev-1", "Improved reporting workflows.")],
    )

    assert result["failed_bullets"] == [
        {
            "bullet": "Improved reporting workflows.",
            "reason": "Linked evidence not found.",
        }
    ]
    assert result["hallucination_count"] == 1


def test_stopwords_ignored() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {
                    "text": "The and with of in to for is was on at by.",
                    "source_evidence_id": "ev-1",
                }
            ]
        ),
        [make_evidence("ev-1", "The and with of in to for is was on at by.")],
    )

    assert result["passed_bullets"] == []
    assert result["failed_bullets"][0]["reason"] == "No keyword overlap with linked evidence."


def test_minimum_length_enforced() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {
                    "text": "Led CRM QA.",
                    "source_evidence_id": "ev-1",
                }
            ]
        ),
        [make_evidence("ev-1", "Led CRM QA.")],
    )

    assert result["passed_bullets"] == []
    assert result["failed_bullets"][0]["reason"] == "No keyword overlap with linked evidence."


def test_multiple_bullets_mixed_pass_fail() -> None:
    passing_bullet = {
        "text": "Built reporting dashboards.",
        "source_evidence_id": "ev-1",
    }
    failing_bullet = {
        "text": "Managed payroll processing.",
        "source_evidence_id": "ev-2",
    }

    result = check_hallucinations(
        make_ai_output([passing_bullet, failing_bullet]),
        [
            make_evidence("ev-1", "Created reporting dashboards for leadership."),
            make_evidence("ev-2", "Scheduled project meetings."),
        ],
    )

    assert result["passed_bullets"] == [passing_bullet]
    assert result["failed_bullets"] == [
        {
            "bullet": "Managed payroll processing.",
            "reason": "No keyword overlap with linked evidence.",
        }
    ]
    assert result["hallucination_count"] == 1


def test_all_bullets_fail() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {"text": "Managed payroll.", "source_evidence_id": "ev-1"},
                {"text": "Designed training.", "source_evidence_id": "missing"},
            ]
        ),
        [make_evidence("ev-1", "Prepared weekly reports.")],
    )

    assert result["passed_bullets"] == []
    assert result["hallucination_count"] == 2


def test_empty_bullet_list() -> None:
    result = check_hallucinations(make_ai_output([]), [make_evidence("ev-1", "Text")])

    assert result == {
        "passed_bullets": [],
        "failed_bullets": [],
        "hallucination_count": 0,
    }


def test_empty_evidence_database() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {
                    "text": "Improved reporting workflows.",
                    "source_evidence_id": "ev-1",
                }
            ]
        ),
        [],
    )

    assert result["failed_bullets"] == [
        {
            "bullet": "Improved reporting workflows.",
            "reason": "Linked evidence not found.",
        }
    ]
    assert result["hallucination_count"] == 1


def test_correct_hallucination_count() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {"text": "Created dashboards.", "source_evidence_id": "ev-1"},
                {"text": "Managed benefits.", "source_evidence_id": "ev-1"},
                {"text": "Led audits.", "source_evidence_id": "missing"},
            ]
        ),
        [make_evidence("ev-1", "Created dashboards for operations.")],
    )

    assert result["hallucination_count"] == 2


def test_exact_matching_no_substring_match() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {
                    "text": "Created report metric.",
                    "source_evidence_id": "ev-1",
                }
            ]
        ),
        [make_evidence("ev-1", "Built reporting metrics.")],
    )

    assert result["passed_bullets"] == []
    assert result["failed_bullets"] == [
        {
            "bullet": "Created report metric.",
            "reason": "No keyword overlap with linked evidence.",
        }
    ]


def test_no_plural_stemming_in_v1() -> None:
    result = check_hallucinations(
        make_ai_output(
            [
                {
                    "text": "Completed stakeholder alignment.",
                    "source_evidence_id": "ev-1",
                }
            ]
        ),
        [make_evidence("ev-1", "Managed stakeholders.")],
    )

    assert result["passed_bullets"] == []
    assert result["failed_bullets"] == [
        {
            "bullet": "Completed stakeholder alignment.",
            "reason": "No keyword overlap with linked evidence.",
        }
    ]
