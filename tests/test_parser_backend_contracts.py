"""
Test Parser Backend Contracts

Purpose:
Verify deterministic parser outputs are compatible with existing backend
contracts before UI integration.
"""

from dataclasses import fields
import json
from pathlib import Path

from engine.candidate_profile_text_parser import parse_candidate_profile_text
from engine.evidence_extractor import extract_evidence
from engine.job_description_text_parser import parse_job_description_text
from engine.resume_analysis_orchestrator import _is_empty_profile, run_resume_analysis
from models.job_description import JobDescription


SAMPLE_PROFILE_PATH = Path("samples/sample_profile_admin.json")


def valid_cv_text() -> str:
    """Return a short realistic CV text fixture."""
    return """
Jane Admin
Contact
jane.admin@example.com
+971 50 123 4567

Skills
- Documentation

Work Experience
- Coordinated office documentation and maintained administrative records.

Certifications
- Certified Administrative Professional
"""


def valid_jd_text() -> str:
    """Return a short realistic JD text fixture."""
    return """
Job Title:
Administrative Assistant

Responsibilities
- Maintain documentation and administrative records.

Required Skills
- Documentation
- Microsoft Excel

Requirements
- Administrative office support experience

Experience
Mid level administrative experience

Education
Bachelor's degree
"""


def parsed_candidate_profile() -> dict:
    """Return parser-produced candidate profile payload."""
    result = parse_candidate_profile_text(valid_cv_text())
    assert result["status"] == "success"
    return result["candidate_profile"]


def parsed_job_description() -> dict:
    """Return parser-produced job description payload."""
    result = parse_job_description_text(valid_jd_text())
    assert result["status"] == "success"
    return result["job_description"]


def test_jd_parser_result_shape_matches_job_description_contract() -> None:
    result = parse_job_description_text(valid_jd_text())
    job_description = result["job_description"]

    assert result["status"] == "success"
    assert isinstance(job_description, dict)
    assert set(job_description) == {field.name for field in fields(JobDescription)}


def test_jd_dataclass_conversion_succeeds() -> None:
    job_description = JobDescription(**parsed_job_description())

    assert job_description.job_title == "Administrative Assistant"
    assert job_description.required_skills == ["Documentation", "Microsoft Excel"]


def test_jd_dataclass_field_compatibility_allows_no_extra_keys() -> None:
    parsed_jd = parsed_job_description()
    valid_fields = {field.name for field in fields(JobDescription)}

    assert set(parsed_jd).issubset(valid_fields)


def test_candidate_parser_result_shape_matches_sample_profile_contract() -> None:
    result = parse_candidate_profile_text(valid_cv_text())
    sample_profile = json.loads(SAMPLE_PROFILE_PATH.read_text(encoding="utf-8"))

    assert result["status"] == "success"
    assert isinstance(result["candidate_profile"], dict)
    assert set(result["candidate_profile"]) == set(sample_profile)


def test_candidate_experience_entry_shape_matches_backend_expectation() -> None:
    candidate_profile = parsed_candidate_profile()

    assert isinstance(candidate_profile["experience"], list)
    for entry in candidate_profile["experience"]:
        assert isinstance(entry, dict)
        assert {"id", "text", "skills"}.issubset(entry)


def test_candidate_profile_is_not_empty_for_existing_backend_logic() -> None:
    candidate_profile = parsed_candidate_profile()

    assert _is_empty_profile(candidate_profile) is False


def test_evidence_extraction_compatibility_with_parsed_candidate_profile() -> None:
    evidence_items = extract_evidence(parsed_candidate_profile())

    assert isinstance(evidence_items, list)
    assert evidence_items
    for evidence in evidence_items:
        assert hasattr(evidence, "text")
        assert hasattr(evidence, "source_type")


def test_orchestrator_compatibility_smoke_path_with_parser_outputs() -> None:
    candidate_profile = parsed_candidate_profile()
    job_description = JobDescription(**parsed_job_description())

    result = run_resume_analysis(candidate_profile, job_description)

    assert isinstance(result, dict)
    assert {
        "status",
        "match_score",
        "final_resume",
        "final_resume_validation",
        "failed_stage",
        "completed_stages",
        "errors",
    }.issubset(result)


def test_no_invention_preserved_between_candidate_and_jd_parser_contracts() -> None:
    candidate_profile = parsed_candidate_profile()
    job_description = parsed_job_description()

    assert candidate_profile["skills"] == ["Documentation"]
    assert "Microsoft Excel" in job_description["required_skills"]
    assert "Microsoft Excel" not in candidate_profile["skills"]
