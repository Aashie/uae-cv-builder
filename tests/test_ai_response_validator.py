"""
Test AI Response Validator

Purpose:
Unit tests for AI Generation Contract structural validation.
"""

from engine.ai_response_validator import validate_ai_response


def valid_response() -> dict:
    """Return a valid AI response fixture."""
    return {
        "summary": "Experienced operations coordinator.",
        "experience_bullets": [
            {
                "text": "Improved reporting workflows.",
                "source_evidence_id": "ev-1",
            }
        ],
        "skills": {
            "technical": ["Excel"],
            "soft": ["Communication"],
            "domain": ["Operations"],
        },
    }


def test_valid_response_passes_all_checks() -> None:
    result = validate_ai_response(valid_response())

    assert result == {"is_valid": True, "errors": []}


def test_missing_summary() -> None:
    response = valid_response()
    response.pop("summary")

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Missing required field: summary" in result["errors"]


def test_missing_experience_bullets() -> None:
    response = valid_response()
    response.pop("experience_bullets")

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Missing required field: experience_bullets" in result["errors"]


def test_missing_skills() -> None:
    response = valid_response()
    response.pop("skills")

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Missing required field: skills" in result["errors"]


def test_empty_summary() -> None:
    response = valid_response()
    response["summary"] = " "

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Empty required field: summary" in result["errors"]


def test_experience_bullets_is_not_a_list() -> None:
    response = valid_response()
    response["experience_bullets"] = {}

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Invalid type for experience_bullets: expected list" in result["errors"]


def test_bullet_item_is_not_a_dict() -> None:
    response = valid_response()
    response["experience_bullets"] = ["not a dict"]

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Invalid type for bullet at index 0: expected dict" in result["errors"]


def test_missing_bullet_text() -> None:
    response = valid_response()
    response["experience_bullets"][0].pop("text")

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Missing required field: text in bullet at index 0" in result["errors"]


def test_missing_source_evidence_id() -> None:
    response = valid_response()
    response["experience_bullets"][0].pop("source_evidence_id")

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert (
        "Missing required field: source_evidence_id in bullet at index 0"
        in result["errors"]
    )


def test_empty_bullet_text() -> None:
    response = valid_response()
    response["experience_bullets"][0]["text"] = ""

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Empty required field: text in bullet at index 0" in result["errors"]


def test_empty_source_evidence_id() -> None:
    response = valid_response()
    response["experience_bullets"][0]["source_evidence_id"] = " "

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert (
        "Empty required field: source_evidence_id in bullet at index 0"
        in result["errors"]
    )


def test_skills_is_not_a_dict() -> None:
    response = valid_response()
    response["skills"] = []

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Invalid type for skills: expected dict" in result["errors"]


def test_technical_is_not_a_list() -> None:
    response = valid_response()
    response["skills"]["technical"] = "Excel"

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Invalid type for skills.technical: expected list" in result["errors"]


def test_soft_is_not_a_list() -> None:
    response = valid_response()
    response["skills"]["soft"] = "Communication"

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Invalid type for skills.soft: expected list" in result["errors"]


def test_domain_is_not_a_list() -> None:
    response = valid_response()
    response["skills"]["domain"] = "Operations"

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Invalid type for skills.domain: expected list" in result["errors"]


def test_unsupported_top_level_field_present() -> None:
    response = valid_response()
    response["extra"] = "unsupported"

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert "Unsupported field: extra" in result["errors"]


def test_multiple_validation_errors_returned_in_single_pass() -> None:
    response = {
        "summary": "",
        "experience_bullets": [
            "not a dict",
            {"text": "", "source_evidence_id": ""},
            {},
        ],
        "skills": {"technical": "Excel"},
        "extra": True,
    }

    result = validate_ai_response(response)

    assert result["is_valid"] is False
    assert result["errors"] == [
        "Unsupported field: extra",
        "Empty required field: summary",
        "Invalid type for bullet at index 0: expected dict",
        "Empty required field: text in bullet at index 1",
        "Empty required field: source_evidence_id in bullet at index 1",
        "Missing required field: text in bullet at index 2",
        "Missing required field: source_evidence_id in bullet at index 2",
        "Invalid type for skills.technical: expected list",
        "Missing required field: skills.soft",
        "Missing required field: skills.domain",
    ]


def experience_bullets_response() -> dict:
    """Return a valid experience bullet generation response fixture."""
    return {
        "summary": "",
        "experience_bullets": [
            {
                "text": "Coordinated reporting workflows.",
                "source_evidence_id": "EXP001",
            }
        ],
        "skills": {
            "technical": [],
            "soft": [],
            "domain": [],
        },
    }


def test_experience_bullets_context_accepts_empty_summary() -> None:
    result = validate_ai_response(
        experience_bullets_response(),
        context="experience_bullets",
    )

    assert result == {"is_valid": True, "errors": []}


def test_default_context_still_rejects_empty_summary() -> None:
    result = validate_ai_response(experience_bullets_response())

    assert result["is_valid"] is False
    assert "Empty required field: summary" in result["errors"]


def test_experience_bullets_context_still_requires_summary_key() -> None:
    response = experience_bullets_response()
    response.pop("summary")

    result = validate_ai_response(response, context="experience_bullets")

    assert result["is_valid"] is False
    assert "Missing required field: summary" in result["errors"]


def test_experience_bullets_context_rejects_unsupported_top_level_field() -> None:
    response = experience_bullets_response()
    response["extra"] = "unsupported"

    result = validate_ai_response(response, context="experience_bullets")

    assert result["is_valid"] is False
    assert "Unsupported field: extra" in result["errors"]


def test_experience_bullets_context_rejects_invalid_bullet_structure() -> None:
    response = experience_bullets_response()
    response["experience_bullets"] = [{"text": "", "source_evidence_id": ""}]

    result = validate_ai_response(response, context="experience_bullets")

    assert result["is_valid"] is False
    assert "Empty required field: text in bullet at index 0" in result["errors"]
    assert (
        "Empty required field: source_evidence_id in bullet at index 0"
        in result["errors"]
    )


def test_experience_bullets_context_accepts_empty_skill_lists() -> None:
    result = validate_ai_response(
        experience_bullets_response(),
        context="experience_bullets",
    )

    assert result["is_valid"] is True
