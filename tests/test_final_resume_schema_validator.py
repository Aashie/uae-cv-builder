"""
Test Final Resume Schema Validator

Purpose:
Unit tests for deterministic final resume schema validation.
"""

import copy

from engine.final_resume_schema_validator import validate_final_resume


def valid_final_resume() -> dict:
    """Return a valid final_resume fixture matching the assembler output shape."""
    return {
        "job_title": "Operations Coordinator",
        "professional_summary": "Professional summary.",
        "skills": {
            "technical": ["Microsoft Excel"],
            "soft": ["Leadership"],
            "tools": ["CRM"],
            "domain": ["Operations"],
            "matched_skills": ["Microsoft Excel"],
            "strongest_skills": ["Reporting"],
        },
        "experience_bullets": [
            {
                "text": "Coordinated reporting workflows.",
                "source_evidence_id": "EXP001",
            }
        ],
        "metadata": {
            "assembled_by": "resume_output_assembler",
            "version": "v1",
            "summary_source": "ai_generated",
            "bullet_source": "deterministic_evidence",
            "skills_source": "skills_section_generator",
        },
    }


def test_valid_final_resume_passes() -> None:
    result = validate_final_resume(valid_final_resume())

    assert result == {"is_valid": True, "errors": [], "warnings": []}


def test_non_dict_input_fails() -> None:
    result = validate_final_resume([])

    assert result == {
        "is_valid": False,
        "errors": ["final_resume must be a dictionary."],
        "warnings": [],
    }


def test_missing_each_required_top_level_key_fails() -> None:
    required_keys = {
        "job_title",
        "professional_summary",
        "skills",
        "experience_bullets",
        "metadata",
    }

    for key in required_keys:
        final_resume = valid_final_resume()
        final_resume.pop(key)

        result = validate_final_resume(final_resume)

        assert result["is_valid"] is False
        assert f"Missing required section: {key}." in result["errors"]


def test_wrong_type_for_job_title_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["job_title"] = []

    result = validate_final_resume(final_resume)

    assert "Section 'job_title' must be a string." in result["errors"]


def test_wrong_type_for_professional_summary_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = []

    result = validate_final_resume(final_resume)

    assert "Section 'professional_summary' must be a string." in result["errors"]


def test_wrong_type_for_skills_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["skills"] = []

    result = validate_final_resume(final_resume)

    assert "Section 'skills' must be a dictionary." in result["errors"]


def test_wrong_type_for_experience_bullets_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["experience_bullets"] = {}

    result = validate_final_resume(final_resume)

    assert "Section 'experience_bullets' must be a list." in result["errors"]


def test_wrong_type_for_metadata_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["metadata"] = []

    result = validate_final_resume(final_resume)

    assert "Section 'metadata' must be a dictionary." in result["errors"]


def test_missing_each_skills_category_fails() -> None:
    required_skill_keys = {
        "technical",
        "soft",
        "tools",
        "domain",
        "matched_skills",
        "strongest_skills",
    }

    for key in required_skill_keys:
        final_resume = valid_final_resume()
        final_resume["skills"].pop(key)

        result = validate_final_resume(final_resume)

        assert result["is_valid"] is False
        assert f"Missing skills category: {key}." in result["errors"]


def test_non_list_skills_category_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["skills"]["technical"] = "Microsoft Excel"

    result = validate_final_resume(final_resume)

    assert "Skills category 'technical' must be a list." in result["errors"]


def test_empty_professional_summary_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = "   "

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert "Section 'professional_summary' must not be empty." in result["errors"]


def test_short_professional_summary_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = "Short"

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert "Section 'professional_summary' is too weak." in result["errors"]


def test_generic_match_score_summary_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = (
        "Professional with a 28.57% match score for opportunities."
    )

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert (
        "Section 'professional_summary' contains a generic match-score placeholder "
        "or is missing target role context."
        in result["errors"]
    )


def test_generic_match_score_summary_without_period_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = (
        "Professional with a 0% match score for opportunities"
    )

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert (
        "Section 'professional_summary' contains a generic match-score placeholder "
        "or is missing target role context."
        in result["errors"]
    )


def test_empty_title_generic_match_score_summary_with_double_space_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = (
        "Professional with a 28.57% match score for  opportunities."
    )

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert any(
        "generic match-score placeholder" in error
        and "missing target role context" in error
        for error in result["errors"]
    )


def test_empty_title_zero_match_score_summary_with_double_space_fails() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = (
        "Professional with a 0% match score for  opportunities."
    )

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert any(
        "generic match-score placeholder" in error
        and "missing target role context" in error
        for error in result["errors"]
    )


def test_match_score_summary_with_target_role_passes() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = (
        "Professional with a 75% match score for Sales Executive opportunities."
    )

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is True


def test_normal_candidate_safe_summary_passes() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = (
        "Sales-focused professional with UAE client communication experience "
        "and Microsoft Office skills."
    )

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is True


def test_legitimate_summary_with_percentage_passes() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = (
        "Improved reporting accuracy by 20% while coordinating operations workflows."
    )

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is True


def test_empty_skills_lists_fail() -> None:
    final_resume = valid_final_resume()
    final_resume["skills"] = {
        "technical": [],
        "soft": [],
        "tools": [],
        "domain": [],
        "matched_skills": [],
        "strongest_skills": [],
    }

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert "Section 'skills' must contain at least one visible skill." in result["errors"]


def test_skills_with_one_visible_skill_pass() -> None:
    final_resume = valid_final_resume()
    final_resume["skills"] = {
        "technical": [],
        "soft": [],
        "tools": ["CRM"],
        "domain": [],
        "matched_skills": [],
        "strongest_skills": [],
    }

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is True


def test_empty_experience_bullets_fail() -> None:
    final_resume = valid_final_resume()
    final_resume["experience_bullets"] = []

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert (
        "Section 'experience_bullets' must contain at least one visible bullet."
        in result["errors"]
    )


def test_experience_bullets_with_only_empty_strings_fail() -> None:
    final_resume = valid_final_resume()
    final_resume["experience_bullets"] = ["", "   ", {"text": "  "}]

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is False
    assert (
        "Section 'experience_bullets' must contain at least one visible bullet."
        in result["errors"]
    )


def test_experience_bullets_with_non_empty_string_pass() -> None:
    final_resume = valid_final_resume()
    final_resume["experience_bullets"] = ["Preserved bullet text."]

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is True


def test_useful_final_resume_passes() -> None:
    final_resume = valid_final_resume()
    final_resume["professional_summary"] = (
        "Operations professional with documented reporting and coordination experience."
    )
    final_resume["skills"] = {
        "technical": [],
        "soft": ["Leadership"],
        "tools": [],
        "domain": [],
        "matched_skills": [],
        "strongest_skills": [],
    }
    final_resume["experience_bullets"] = [
        {
            "text": "Coordinated reporting workflows.",
            "source_evidence_id": "EXP001",
        }
    ]

    result = validate_final_resume(final_resume)

    assert result["is_valid"] is True


def test_warnings_key_is_always_present_and_empty() -> None:
    valid_result = validate_final_resume(valid_final_resume())
    invalid_result = validate_final_resume(None)

    assert valid_result["warnings"] == []
    assert invalid_result["warnings"] == []


def test_validator_does_not_mutate_input() -> None:
    final_resume = valid_final_resume()
    original = copy.deepcopy(final_resume)

    validate_final_resume(final_resume)

    assert final_resume == original
