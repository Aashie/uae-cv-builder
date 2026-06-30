"""
Test Evidence Model

Purpose:
Unit tests for the Evidence dataclass and its serialization helpers.
"""

from models.evidence import Evidence


def test_evidence_object_creation():
    evidence = Evidence(
        id="ev-001",
        source_type="experience",
        source_id="exp-001",
        category="achievement",
        text="Managed high-volume operations across three departments.",
        skills=["Operations Management", "Data Analysis"],
    )

    assert evidence.id == "ev-001"
    assert evidence.source_type == "experience"
    assert evidence.source_id == "exp-001"
    assert evidence.category == "achievement"
    assert evidence.text == "Managed high-volume operations across three departments."
    assert evidence.skills == ["Operations Management", "Data Analysis"]
    assert evidence.confidence == 1.0


def test_evidence_to_dict():
    evidence = Evidence(
        id="ev-002",
        source_type="project",
        source_id="proj-001",
        category="outcome",
        text="Built an internal dashboard reducing reporting time by 40%.",
        skills=["Python", "Dashboard Design"],
        confidence=0.95,
    )

    result = evidence.to_dict()

    assert result == {
        "id": "ev-002",
        "source_type": "project",
        "source_id": "proj-001",
        "category": "outcome",
        "text": "Built an internal dashboard reducing reporting time by 40%.",
        "skills": ["Python", "Dashboard Design"],
        "confidence": 0.95,
    }
