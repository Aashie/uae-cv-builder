"""
Test Resume Export Adapter

Purpose:
Unit tests for deterministic final_resume export payload adaptation.
"""

import copy

from engine.resume_export_adapter import build_resume_export_payload


def valid_final_resume() -> dict:
    """Return a valid final_resume fixture."""
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
        },
    }


def section_by_id(payload: dict, section_id: str) -> dict:
    """Return a payload section by id."""
    return next(section for section in payload["sections"] if section["id"] == section_id)


def test_valid_final_resume_builds_successful_export_payload() -> None:
    payload = build_resume_export_payload(valid_final_resume())

    assert payload["status"] == "success"
    assert payload["errors"] == []
    assert payload["sections"]


def test_invalid_final_resume_returns_failed_payload_with_validation_errors() -> None:
    payload = build_resume_export_payload({})

    assert payload["status"] == "failed"
    assert "Missing required section: job_title." in payload["errors"]
    assert payload["document_title"] == ""
    assert payload["sections"] == []


def test_document_title_maps_from_job_title() -> None:
    payload = build_resume_export_payload(valid_final_resume())

    assert payload["document_title"] == "Operations Coordinator"


def test_professional_summary_section_maps_correctly() -> None:
    payload = build_resume_export_payload(valid_final_resume())

    assert section_by_id(payload, "professional_summary") == {
        "id": "professional_summary",
        "title": "Professional Summary",
        "type": "paragraph",
        "content": "Professional summary.",
    }


def test_skills_section_maps_visible_categories_only() -> None:
    payload = build_resume_export_payload(valid_final_resume())

    assert section_by_id(payload, "skills")["content"] == {
        "Technical": ["Microsoft Excel"],
        "Soft Skills": ["Leadership"],
        "Tools": ["CRM"],
        "Domain": ["Operations"],
    }


def test_matched_and_strongest_skills_are_not_visible_groups() -> None:
    payload = build_resume_export_payload(valid_final_resume())
    visible_groups = section_by_id(payload, "skills")["content"]

    assert "matched_skills" not in visible_groups
    assert "strongest_skills" not in visible_groups
    assert "Matched Skills" not in visible_groups
    assert "Strongest Skills" not in visible_groups


def test_experience_bullet_dictionaries_export_text_only() -> None:
    payload = build_resume_export_payload(valid_final_resume())

    assert section_by_id(payload, "experience")["content"] == [
        "Coordinated reporting workflows."
    ]


def test_source_evidence_id_is_not_exposed() -> None:
    payload = build_resume_export_payload(valid_final_resume())
    experience_content = section_by_id(payload, "experience")["content"]

    assert "EXP001" not in experience_content


def test_string_experience_bullets_are_supported() -> None:
    final_resume = valid_final_resume()
    final_resume["experience_bullets"] = ["Preserved bullet text."]

    payload = build_resume_export_payload(final_resume)

    assert section_by_id(payload, "experience")["content"] == [
        "Preserved bullet text."
    ]


def test_metadata_contains_adapter_version_source_and_source_metadata() -> None:
    final_resume = valid_final_resume()

    payload = build_resume_export_payload(final_resume)

    assert payload["metadata"] == {
        "adapter": "resume_export_adapter",
        "version": "v1",
        "source": "final_resume",
        "source_metadata": final_resume["metadata"],
    }


def test_adapter_does_not_mutate_input() -> None:
    final_resume = valid_final_resume()
    original = copy.deepcopy(final_resume)

    build_resume_export_payload(final_resume)

    assert final_resume == original


def test_empty_but_valid_sections_export_successfully() -> None:
    final_resume = valid_final_resume()
    final_resume["job_title"] = ""
    final_resume["professional_summary"] = ""
    final_resume["skills"] = {
        "technical": [],
        "soft": [],
        "tools": [],
        "domain": [],
        "matched_skills": [],
        "strongest_skills": [],
    }
    final_resume["experience_bullets"] = []

    payload = build_resume_export_payload(final_resume)

    assert payload["status"] == "success"
    assert payload["document_title"] == ""
    assert section_by_id(payload, "experience")["content"] == []


def test_payload_sections_appear_in_stable_order() -> None:
    payload = build_resume_export_payload(valid_final_resume())

    assert [section["id"] for section in payload["sections"]] == [
        "professional_summary",
        "skills",
        "experience",
    ]


def test_no_nested_payload_wrapper_exists() -> None:
    payload = build_resume_export_payload(valid_final_resume())

    assert "payload" not in payload
