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
    assert result["final_resume"]


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
    def fail_summary_validation(ai_output, context="full_resume"):
        if context == "full_resume":
            return {"is_valid": False, "errors": ["bad ai"]}
        return {"is_valid": True, "errors": []}

    monkeypatch.setattr(
        orchestrator,
        "validate_ai_response",
        fail_summary_validation,
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert result["ai_validation"] == {"is_valid": False, "errors": ["bad ai"]}
    assert "Professional summary validation failed: ['bad ai']" in result["errors"]


def test_bullet_validation_failure_skips_hallucination_checker(monkeypatch) -> None:
    calls = []

    def fail_bullet_validation(ai_output, context="full_resume"):
        if context == "experience_bullets":
            return {"is_valid": False, "errors": ["bad bullets"]}
        return {"is_valid": True, "errors": []}

    monkeypatch.setattr(
        orchestrator,
        "validate_ai_response",
        fail_bullet_validation,
    )
    monkeypatch.setattr(
        orchestrator,
        "check_hallucinations",
        lambda ai_output, evidence_items: calls.append("called"),
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert calls == []
    assert result["status"] == "partial"
    assert "Experience bullet validation failed: ['bad bullets']" in result["errors"]
    assert result["hallucination_check"] == {
        "passed_bullets": [],
        "failed_bullets": [],
        "hallucination_count": 0,
    }
    assert result["experience_bullet_output"]["ai_output"]["experience_bullets"] == []


def test_hallucination_checker_failure_creates_partial_status(monkeypatch) -> None:
    monkeypatch.setattr(
        orchestrator,
        "generate_experience_bullets",
        lambda evidence_items: {
            "status": "success",
            "errors": [],
            "provider": "gemini",
            "mode": "deterministic",
            "ai_output": {
                "summary": "",
                "experience_bullets": [
                    {"text": "Unsupported claim.", "source_evidence_id": "missing"}
                ],
                "skills": {"technical": [], "soft": [], "domain": []},
            },
        },
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert result["hallucination_check"]["hallucination_count"] == 1
    assert "Hallucination checker removed unsupported bullets." in result["errors"]


def test_safety_layer_output_included() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["ai_validation"] == {"is_valid": True, "errors": []}
    assert result["experience_bullet_validation"] == {"is_valid": True, "errors": []}
    assert result["hallucination_check"] == {
        "passed_bullets": result["experience_bullet_output"]["ai_output"][
            "experience_bullets"
        ],
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
        "experience_bullet_output",
        "experience_bullet_validation",
        "hallucination_check",
        "resume_output",
        "final_resume",
    }


def test_orchestrator_calls_experience_bullet_generator(monkeypatch) -> None:
    calls = []

    def fake_generator(evidence_items):
        calls.append(evidence_items)
        return {
            "status": "success",
            "errors": [],
            "provider": "gemini",
            "mode": "deterministic",
            "ai_output": {
                "summary": "",
                "experience_bullets": [],
                "skills": {"technical": [], "soft": [], "domain": []},
            },
        }

    monkeypatch.setattr(orchestrator, "generate_experience_bullets", fake_generator)

    orchestrator.run_resume_analysis(make_profile(), make_job())

    assert len(calls) == 1


def test_orchestrator_validates_experience_bullets_with_context(monkeypatch) -> None:
    contexts = []

    def track_validation(ai_output, context="full_resume"):
        contexts.append(context)
        return {"is_valid": True, "errors": []}

    monkeypatch.setattr(orchestrator, "validate_ai_response", track_validation)

    orchestrator.run_resume_analysis(make_profile(), make_job())

    assert "full_resume" in contexts
    assert "experience_bullets" in contexts


def test_orchestrator_runs_hallucination_checker_after_bullet_validation(monkeypatch) -> None:
    events = []

    def track_validation(ai_output, context="full_resume"):
        if context == "experience_bullets":
            events.append("bullet_validation")
        return {"is_valid": True, "errors": []}

    def track_hallucination(ai_output, evidence_items):
        events.append("hallucination")
        return {
            "passed_bullets": ai_output["experience_bullets"],
            "failed_bullets": [],
            "hallucination_count": 0,
        }

    monkeypatch.setattr(orchestrator, "validate_ai_response", track_validation)
    monkeypatch.setattr(orchestrator, "check_hallucinations", track_hallucination)

    orchestrator.run_resume_analysis(make_profile(), make_job())

    assert events == ["bullet_validation", "hallucination"]


def test_orchestrator_calls_resume_output_assembler(monkeypatch) -> None:
    calls = []

    def fake_assembler(resume_draft, professional_summary_output, experience_bullet_output):
        calls.append((resume_draft, professional_summary_output, experience_bullet_output))
        return {
            "status": "success",
            "errors": [],
            "final_resume": {"job_title": "Assembled"},
        }

    monkeypatch.setattr(orchestrator, "assemble_resume_output", fake_assembler)

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert len(calls) == 1
    assert result["final_resume"] == {"job_title": "Assembled"}


def test_experience_bullet_output_exists() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert "experience_bullet_output" in result
    assert result["experience_bullet_output"]["status"] == "success"


def test_experience_bullet_validation_exists() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["experience_bullet_validation"] == {"is_valid": True, "errors": []}


def test_resume_output_exists() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["resume_output"]["status"] == "success"


def test_final_resume_exists() -> None:
    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["final_resume"] == result["resume_output"]["final_resume"]


def test_experience_bullet_generator_failure_marks_partial(monkeypatch) -> None:
    monkeypatch.setattr(
        orchestrator,
        "generate_experience_bullets",
        lambda evidence_items: {
            "status": "failed",
            "errors": ["no evidence"],
            "provider": "gemini",
            "mode": "deterministic",
            "ai_output": {
                "summary": "",
                "experience_bullets": [],
                "skills": {"technical": [], "soft": [], "domain": []},
            },
        },
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert "Experience bullet generation failed." in result["errors"]


def test_experience_bullet_validation_failure_marks_partial(monkeypatch) -> None:
    def fail_bullet_validation(ai_output, context="full_resume"):
        if context == "experience_bullets":
            return {"is_valid": False, "errors": ["bad bullets"]}
        return {"is_valid": True, "errors": []}

    monkeypatch.setattr(orchestrator, "validate_ai_response", fail_bullet_validation)

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert "Experience bullet validation failed: ['bad bullets']" in result["errors"]


def test_hallucination_failure_passes_only_passed_bullets_to_assembler(monkeypatch) -> None:
    approved_bullet = {
        "text": "Used Excel to coordinate reporting.",
        "source_evidence_id": "EXP001",
    }
    captured = {}

    monkeypatch.setattr(
        orchestrator,
        "check_hallucinations",
        lambda ai_output, evidence_items: {
            "passed_bullets": [approved_bullet],
            "failed_bullets": [{"bullet": "Unsupported", "reason": "No overlap"}],
            "hallucination_count": 1,
        },
    )

    def capture_assembler(resume_draft, professional_summary_output, experience_bullet_output):
        captured["bullets"] = experience_bullet_output["ai_output"]["experience_bullets"]
        return {
            "status": "success",
            "errors": [],
            "final_resume": {"experience_bullets": captured["bullets"]},
        }

    monkeypatch.setattr(orchestrator, "assemble_resume_output", capture_assembler)

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert captured["bullets"] == [approved_bullet]


def test_all_hallucinated_bullets_results_in_empty_bullets(monkeypatch) -> None:
    captured = {}
    monkeypatch.setattr(
        orchestrator,
        "check_hallucinations",
        lambda ai_output, evidence_items: {
            "passed_bullets": [],
            "failed_bullets": [{"bullet": "Unsupported", "reason": "No overlap"}],
            "hallucination_count": 1,
        },
    )

    def capture_assembler(resume_draft, professional_summary_output, experience_bullet_output):
        captured["bullets"] = experience_bullet_output["ai_output"]["experience_bullets"]
        return {
            "status": "success",
            "errors": [],
            "final_resume": {"experience_bullets": captured["bullets"]},
        }

    monkeypatch.setattr(orchestrator, "assemble_resume_output", capture_assembler)

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert captured["bullets"] == []


def test_assembler_partial_status_marks_orchestrator_partial(monkeypatch) -> None:
    monkeypatch.setattr(
        orchestrator,
        "assemble_resume_output",
        lambda resume_draft, summary_output, bullet_output: {
            "status": "partial",
            "errors": ["assembler warning"],
            "final_resume": {},
        },
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert "Resume output assembly returned partial status." in result["errors"]
    assert "assembler warning" in result["errors"]


def test_assembler_failed_status_marks_orchestrator_partial(monkeypatch) -> None:
    monkeypatch.setattr(
        orchestrator,
        "assemble_resume_output",
        lambda resume_draft, summary_output, bullet_output: {
            "status": "failed",
            "errors": ["assembler failed"],
            "final_resume": {},
        },
    )

    result = orchestrator.run_resume_analysis(make_profile(), make_job())

    assert result["status"] == "partial"
    assert "Resume output assembly failed." in result["errors"]


def test_career_insights_still_runs_immediately_after_evidence_extractor(monkeypatch) -> None:
    events = []

    def track_extract(profile):
        events.append("extract")
        return []

    def track_career(evidence_items):
        events.append("career")
        return {
            "strongest_skills": [],
            "skill_frequency": {},
            "total_evidence_items": 0,
            "total_unique_skills": 0,
        }

    def track_match(job_description, profile_skills, evidence_items):
        events.append("matcher")
        return {
            "matched_skills": ["Excel"],
            "missing_skills": [],
            "evidence_matches": {},
            "score": 100,
        }

    monkeypatch.setattr(orchestrator, "extract_evidence", track_extract)
    monkeypatch.setattr(orchestrator, "analyze_career_insights", track_career)
    monkeypatch.setattr(orchestrator, "match_job_to_profile", track_match)

    orchestrator.run_resume_analysis(make_profile(), make_job())

    assert events[:3] == ["extract", "career", "matcher"]
