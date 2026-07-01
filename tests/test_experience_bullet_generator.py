"""
Test Experience Bullet Generator

Purpose:
Unit tests for deterministic evidence-safe experience bullet generation.
"""

import pytest

from engine.experience_bullet_generator import generate_experience_bullets
from engine.hallucination_checker import check_hallucinations
from models.evidence import Evidence


def make_evidence(
    evidence_id: str,
    text: str,
    category: str = "experience",
) -> Evidence:
    """Create a minimal Evidence object for generator tests."""
    return Evidence(
        id=evidence_id,
        source_type=category,
        source_id=evidence_id.lower(),
        category=category,
        text=text,
        skills=[],
    )


def test_successful_bullet_generation() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")]
    )

    assert result["status"] == "success"
    assert result["ai_output"]["experience_bullets"] == [
        {
            "text": "Coordinated reporting workflows.",
            "source_evidence_id": "EXP001",
        }
    ]


def test_output_wrapper_contains_required_keys() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")]
    )

    assert set(result) == {"status", "errors", "provider", "mode", "ai_output"}
    assert result["provider"] == "gemini"
    assert result["mode"] == "deterministic"


def test_ai_output_follows_contract_shape() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")]
    )

    assert set(result["ai_output"]) == {"summary", "experience_bullets", "skills"}
    assert set(result["ai_output"]["skills"]) == {"technical", "soft", "domain"}


def test_summary_is_empty_by_design() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")]
    )

    assert result["ai_output"]["summary"] == ""


def test_skills_lists_are_empty_by_design() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")]
    )

    assert result["ai_output"]["skills"] == {
        "technical": [],
        "soft": [],
        "domain": [],
    }


def test_uses_evidence_objects_only() -> None:
    evidence = make_evidence("EXP001", "Coordinated reporting workflows.")

    result = generate_experience_bullets([evidence])

    assert result["ai_output"]["experience_bullets"][0]["text"] == evidence.text
    assert result["ai_output"]["experience_bullets"][0]["source_evidence_id"] == evidence.id


def test_filters_only_experience_evidence() -> None:
    result = generate_experience_bullets(
        [
            make_evidence("PRJ001", "Built project dashboard.", "project"),
            make_evidence("EXP001", "Coordinated reporting workflows.", "experience"),
        ]
    )

    assert result["ai_output"]["experience_bullets"] == [
        {
            "text": "Coordinated reporting workflows.",
            "source_evidence_id": "EXP001",
        }
    ]


def test_ignores_project_evidence() -> None:
    result = generate_experience_bullets(
        [make_evidence("PRJ001", "Built project dashboard.", "project")]
    )

    assert result["status"] == "failed"


def test_ignores_certification_evidence() -> None:
    result = generate_experience_bullets(
        [make_evidence("CERT001", "Completed certification.", "certification")]
    )

    assert result["status"] == "failed"


def test_ignores_achievement_evidence() -> None:
    result = generate_experience_bullets(
        [make_evidence("ACH001", "Won achievement award.", "achievement")]
    )

    assert result["status"] == "failed"


def test_generates_maximum_5_bullets() -> None:
    evidence_items = [
        make_evidence(f"EXP00{index}", f"Coordinated workflow {index}.")
        for index in range(1, 7)
    ]

    result = generate_experience_bullets(evidence_items)

    assert len(result["ai_output"]["experience_bullets"]) == 5


def test_selects_first_5_usable_experience_items_by_list_order() -> None:
    evidence_items = [
        make_evidence(f"EXP00{index}", f"Coordinated workflow {index}.")
        for index in range(1, 7)
    ]

    result = generate_experience_bullets(evidence_items)

    assert [
        bullet["source_evidence_id"]
        for bullet in result["ai_output"]["experience_bullets"]
    ] == ["EXP001", "EXP002", "EXP003", "EXP004", "EXP005"]


def test_generates_all_bullets_for_1_to_4_usable_items() -> None:
    result = generate_experience_bullets(
        [
            make_evidence("EXP001", "Coordinated reporting workflows."),
            make_evidence("EXP002", "Managed client communication."),
            make_evidence("EXP003", "Prepared weekly schedules."),
        ]
    )

    assert len(result["ai_output"]["experience_bullets"]) == 3


def test_no_padding_when_fewer_than_5_items_exist() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")]
    )

    assert len(result["ai_output"]["experience_bullets"]) == 1


def test_zero_experience_evidence_returns_failed_status() -> None:
    result = generate_experience_bullets(
        [make_evidence("PRJ001", "Built project dashboard.", "project")]
    )

    assert result == {
        "status": "failed",
        "errors": ["No experience evidence found. Cannot generate bullets."],
        "provider": "gemini",
        "mode": "deterministic",
        "ai_output": {
            "summary": "",
            "experience_bullets": [],
            "skills": {"technical": [], "soft": [], "domain": []},
        },
    }


def test_none_evidence_items_returns_failed_status() -> None:
    result = generate_experience_bullets(None)

    assert result["status"] == "failed"
    assert result["errors"] == ["No experience evidence found. Cannot generate bullets."]


def test_empty_evidence_items_returns_failed_status() -> None:
    result = generate_experience_bullets([])

    assert result["status"] == "failed"
    assert result["errors"] == ["No experience evidence found. Cannot generate bullets."]


def test_bullet_includes_source_evidence_id() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")]
    )

    assert result["ai_output"]["experience_bullets"][0]["source_evidence_id"] == "EXP001"


def test_bullet_text_is_non_empty() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")]
    )

    assert result["ai_output"]["experience_bullets"][0]["text"]


def test_unsupported_provider_raises_value_error() -> None:
    with pytest.raises(ValueError):
        generate_experience_bullets(
            [make_evidence("EXP001", "Coordinated reporting workflows.")],
            provider="unsupported",
        )


def test_deterministic_gemini_provider_path_works_without_real_api_call() -> None:
    result = generate_experience_bullets(
        [make_evidence("EXP001", "Coordinated reporting workflows.")],
        provider="gemini",
    )

    assert result["status"] == "success"
    assert result["mode"] == "deterministic"


def test_generated_bullets_pass_hallucination_checker() -> None:
    evidence_items = [
        make_evidence("EXP001", "Coordinated reporting workflows for leadership.")
    ]
    result = generate_experience_bullets(evidence_items)

    hallucination_result = check_hallucinations(result["ai_output"], evidence_items)

    assert hallucination_result == {
        "passed_bullets": result["ai_output"]["experience_bullets"],
        "failed_bullets": [],
        "hallucination_count": 0,
    }
