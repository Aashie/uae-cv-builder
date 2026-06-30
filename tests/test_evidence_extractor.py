"""
Test Evidence Extractor

Purpose:
Unit tests for converting profile data into Evidence objects.
"""

from models.evidence import Evidence
from engine.evidence_extractor import extract_evidence


def _sample_profile() -> dict:
    return {
        "experience": [
            {
                "id": "exp-1",
                "title": "Operations Manager",
                "company": "Acme Corp",
                "skills": ["Operations Management", "Leadership"],
            },
            {
                "role": "Administrator",
                "skills": ["Administration"],
            },
        ],
        "projects": [
            {
                "id": "proj-1",
                "name": "AI Career Platform",
                "skills": ["Python", "AI"],
            }
        ],
        "certifications": [
            {
                "name": "PMP Certification",
                "issuer": "PMI",
            }
        ],
        "achievements": [
            {
                "text": "Reduced reporting time by 40%.",
                "skills": ["Process Improvement"],
            }
        ],
    }


def test_extract_evidence_returns_evidence_objects():
    result = extract_evidence(_sample_profile())

    assert isinstance(result, list)
    assert len(result) == 5
    assert all(isinstance(item, Evidence) for item in result)


def test_extract_evidence_generates_correct_ids():
    result = extract_evidence(_sample_profile())
    ids = [item.id for item in result]

    assert ids == ["EXP001", "EXP002", "PRJ001", "CERT001", "ACH001"]


def test_extract_evidence_maps_fields():
    result = extract_evidence(_sample_profile())

    assert result[0].source_type == "experience"
    assert result[0].source_id == "exp-1"
    assert result[0].category == "experience"
    assert result[0].text == "Operations Manager"
    assert result[0].skills == ["Operations Management", "Leadership"]

    assert result[1].source_id == "1"
    assert result[1].text == "Administrator"

    assert result[2].source_type == "project"
    assert result[2].source_id == "proj-1"
    assert result[2].text == "AI Career Platform"

    assert result[3].source_type == "certification"
    assert result[3].text == "PMP Certification"
    assert result[3].skills == []

    assert result[4].source_type == "achievement"
    assert result[4].text == "Reduced reporting time by 40%."
    assert result[4].skills == ["Process Improvement"]


def test_extract_evidence_empty_profile():
    assert extract_evidence({}) == []
    assert extract_evidence(
        {
            "experience": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
        }
    ) == []
