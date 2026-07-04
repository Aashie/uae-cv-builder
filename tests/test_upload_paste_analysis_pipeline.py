"""
Test Upload/Paste Analysis Pipeline

Purpose:
Unit tests for parser-gated backend upload/paste analysis flow.
"""

import engine.upload_paste_analysis_pipeline as pipeline
from engine.upload_paste_analysis_pipeline import run_upload_paste_analysis


TOP_LEVEL_KEYS = {
    "status",
    "candidate_parse_result",
    "job_parse_result",
    "analysis_result",
    "errors",
    "warnings",
    "metadata",
}


def valid_cv_text() -> str:
    """Return a short extracted CV text fixture."""
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
    """Return a short pasted JD text fixture."""
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


def warning_cv_text() -> str:
    """Return parser-success CV text with missing optional sections."""
    return """
Jane Admin
Skills
- Documentation
Work Experience
- Prepared documentation.
"""


def warning_jd_text() -> str:
    """Return parser-success JD text with warnings but required skills."""
    return """
Job Title: Administrative Assistant
Required Skills
- Documentation
"""


def assert_top_level_shape(result: dict) -> None:
    """Assert helper top-level shape."""
    assert set(result) == TOP_LEVEL_KEYS


def test_successful_real_path_helper_result() -> None:
    result = run_upload_paste_analysis(valid_cv_text(), valid_jd_text())

    assert isinstance(result, dict)
    assert_top_level_shape(result)
    assert result["status"] == "success"
    assert result["metadata"]["analysis_ran"] is True
    assert result["metadata"]["completed_stages"] == [
        "candidate_profile_parse",
        "job_description_parse",
        "job_description_model_conversion",
        "resume_analysis",
    ]
    assert result["metadata"]["failed_stage"] == ""


def test_candidate_parser_failure_gates_later_stages() -> None:
    result = run_upload_paste_analysis("   ", valid_jd_text())

    assert result["status"] == "failed"
    assert result["metadata"]["failed_stage"] == "candidate_profile_parse"
    assert result["job_parse_result"] == {}
    assert result["analysis_result"] == {}
    assert result["metadata"]["analysis_ran"] is False


def test_jd_parser_failure_prevents_analysis() -> None:
    result = run_upload_paste_analysis(valid_cv_text(), "   ")

    assert result["status"] == "failed"
    assert result["metadata"]["failed_stage"] == "job_description_parse"
    assert result["candidate_parse_result"]["status"] == "success"
    assert result["analysis_result"] == {}
    assert result["metadata"]["analysis_ran"] is False


def test_jd_dataclass_conversion_failure_prevents_analysis(monkeypatch) -> None:
    monkeypatch.setattr(
        pipeline,
        "parse_job_description_text",
        lambda job_text: {
            "status": "success",
            "job_description": {"unexpected_key": "bad"},
            "errors": [],
            "warnings": [],
            "metadata": {},
        },
    )

    result = run_upload_paste_analysis(valid_cv_text(), valid_jd_text())

    assert result["status"] == "failed"
    assert result["metadata"]["failed_stage"] == "job_description_model_conversion"
    assert result["analysis_result"] == {}
    assert any("JobDescription conversion failed:" in error for error in result["errors"])


def test_analysis_exception_is_caught_safely(monkeypatch) -> None:
    def fail_analysis(profile, job_description):
        raise RuntimeError("analysis boom")

    monkeypatch.setattr(pipeline, "run_resume_analysis", fail_analysis)

    result = run_upload_paste_analysis(valid_cv_text(), valid_jd_text())

    assert result["status"] == "failed"
    assert result["metadata"]["failed_stage"] == "resume_analysis"
    assert result["metadata"]["analysis_ran"] is False
    assert any("analysis boom" in error for error in result["errors"])


def test_parser_warnings_accumulate_without_blocking_analysis() -> None:
    result = run_upload_paste_analysis(warning_cv_text(), warning_jd_text())

    assert result["status"] == "success"
    assert result["warnings"]
    assert result["metadata"]["analysis_ran"] is True


def test_no_invention_boundary_through_helper() -> None:
    result = run_upload_paste_analysis(valid_cv_text(), valid_jd_text())
    candidate_skills = result["candidate_parse_result"]["candidate_profile"]["skills"]

    assert "Documentation" in candidate_skills
    assert "Microsoft Excel" not in candidate_skills


def test_return_shape_on_every_failure_branch(monkeypatch) -> None:
    candidate_failure = run_upload_paste_analysis("   ", valid_jd_text())
    jd_failure = run_upload_paste_analysis(valid_cv_text(), "   ")

    with monkeypatch.context() as patch:
        patch.setattr(
            pipeline,
            "parse_job_description_text",
            lambda job_text: {
                "status": "success",
                "job_description": {"unexpected_key": "bad"},
                "errors": [],
                "warnings": [],
                "metadata": {},
            },
        )
        model_failure = run_upload_paste_analysis(valid_cv_text(), valid_jd_text())

    with monkeypatch.context() as patch:
        def fail_analysis(profile, job_description):
            raise RuntimeError("analysis boom")

        patch.setattr(pipeline, "run_resume_analysis", fail_analysis)
        analysis_failure = run_upload_paste_analysis(valid_cv_text(), valid_jd_text())

    for result in [candidate_failure, jd_failure, model_failure, analysis_failure]:
        assert_top_level_shape(result)
