"""
Test Resume Analysis Orchestrator

Purpose:
Unit tests for the full resume analysis orchestration pipeline.
"""

from engine import resume_analysis_orchestrator as orchestrator
from models.job_description import JobDescription


def make_job(required_skills: list[str] | None = None) -> JobDescription:
    """Create a minimal job description for orchestrator tests."""
    return JobDescription(
        job_title="Operations Coordinator",
        required_skills=required_skills if required_skills is not None else ["Excel"],
        soft_skills=[],
        experience_level="Mid",
        education="Bachelor's",
    )


def make_profile(skills=None) -> dict:
    """Create a minimal supported profile for orchestrator tests."""
    return {
        "skills": skills if skills is not None else ["Excel"],
        "experience": [
            {
                "id": "exp-1",
                "text": "Used Excel to coordinate reporting.",
                "skills": ["Excel"],
            }
        ],
        "projects": [],
        "certifications": [],
        "achievements": [],
    }


def test_successful_pipeline() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "success"
    assert result["errors"] == []
    assert result["match_score"] == 100
    assert result["matched_skills"] == ["Excel"]
    assert result["summary"]


def test_empty_profile_hard_stop() -> None:
    result = orchestrator.run_resume_analysis({}, make_job())

    assert result["status"] == "failed"
    assert result["errors"] == ["Profile is missing or empty."]
    assert result["match_score"] == 0


def test_missing_job_description_hard_stop() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), None)

    assert result["status"] == "failed"
    assert result["errors"] == ["Job description is missing."]


def test_missing_required_skills_hard_stop() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job([]))

    assert result["status"] == "failed"
    assert result["errors"] == ["Job description has no required skills."]


def test_profile_skills_list_supported() -> None:
    result = orchestrator.run_resume_analysis(make_profile(["Excel"]), make_job())

    assert result["matched_skills"] == ["Excel"]
    assert result["match_score"] == 100


def test_profile_skills_dict_supported() -> None:
    result = orchestrator.run_resume_analysis(
        make_profile({"technical": ["Excel"], "soft": ["Communication"], "tools": ["CRM"]}),
        make_job(["CRM"]),
    )

    assert result["matched_skills"] == ["CRM"]
    assert result["match_score"] == 100


def test_recommendation_engine_soft_failure(monkeypatch) -> None:
    def fail_recommendations(matcher_output, skill_gap_output, score_output):
        raise RuntimeError("boom")

    monkeypatch.setattr(orchestrator, "generate_recommendations", fail_recommendations)

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert result["recommendations"] == {
        "resume_recommendations": [],
        "career_recommendations": [],
    }
    assert result["readiness_tier"] == ""
    assert result["errors"] == ["Recommendation engine failed: boom"]


def test_career_insights_soft_failure(monkeypatch) -> None:
    def fail_career_insights(evidence_items):
        raise RuntimeError("boom")

    monkeypatch.setattr(orchestrator, "analyze_career_insights", fail_career_insights)

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert result["career_insights"] == {
        "strongest_skills": [],
        "skill_frequency": {},
        "total_evidence_items": 0,
        "total_unique_skills": 0,
    }
    assert result["errors"] == ["Career insights failed: boom"]


def test_summary_generator_unexpected_failure_uses_resume_draft_summary(monkeypatch) -> None:
    def fail_summary(prompt_package, resume_draft):
        raise RuntimeError("boom")

    monkeypatch.setattr(orchestrator, "generate_professional_summary", fail_summary)

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert result["summary"] == result["resume_draft"]["professional_summary"]
    assert result["errors"] == ["Professional summary generation failed: boom"]


def test_ai_validator_failure_creates_partial_status(monkeypatch) -> None:
    monkeypatch.setattr(
        orchestrator,
        "validate_ai_response",
        lambda ai_output: {"is_valid": False, "errors": ["bad ai"]},
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert result["ai_validation"] == {"is_valid": False, "errors": ["bad ai"]}
    assert result["errors"] == ["AI validation failed: ['bad ai']"]


def test_ai_validator_failure_skips_hallucination_checker(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        orchestrator,
        "validate_ai_response",
        lambda ai_output: {"is_valid": False, "errors": ["bad ai"]},
    )
    monkeypatch.setattr(
        orchestrator,
        "check_hallucinations",
        lambda ai_output, evidence_items: calls.append("called"),
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert calls == []
    assert result["hallucination_check"] == {
        "passed_bullets": [],
        "failed_bullets": [],
        "hallucination_count": 0,
    }


def test_hallucination_checker_failure_creates_partial_status(monkeypatch) -> None:
    monkeypatch.setattr(
        orchestrator,
        "generate_professional_summary",
        lambda prompt, draft: {
            "summary": "Generated summary.",
            "experience_bullets": [
                {"text": "Unsupported claim.", "source_evidence_id": "missing"}
            ],
            "skills": {"technical": [], "soft": [], "domain": []},
        },
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert result["hallucination_check"]["hallucination_count"] == 1
    assert "Hallucination checker removed unsupported bullets." in result["errors"]


def test_safety_layer_output_included() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["ai_validation"] == {"is_valid": True, "errors": []}
    assert result["hallucination_check"] == {
        "passed_bullets": [],
        "failed_bullets": [],
        "hallucination_count": 0,
    }


def test_success_status_returned() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "success"


def test_partial_status_returned(monkeypatch) -> None:
    monkeypatch.setattr(
        orchestrator,
        "generate_recommendations",
        lambda matcher, gaps, score: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"


def test_failed_status_returned() -> None:
    result = orchestrator.run_resume_analysis(None, make_job())

    assert result["status"] == "failed"


def test_output_schema_contains_required_top_level_fields() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert set(result) == {
        "status",
        "errors",
        "match_score",
        "matched_skills",
        "missing_skills",
        "skill_gaps",
        "recommendations",
        "readiness_tier",
        "career_insights",
        "resume_draft",
        "summary",
        "ai_validation",
        "hallucination_check",
    }
