"""
Test Resume Output Assembler

Purpose:
Unit tests for deterministic final resume output assembly.
"""

import ast
from pathlib import Path

from engine.resume_output_assembler import assemble_resume_output


def resume_draft() -> dict:
    """Return a complete resume draft fixture."""
    return {
        "job_title": "Operations Coordinator",
        "professional_summary": "Draft summary.",
        "key_skills": ["Excel", "Reporting"],
        "matched_skills": ["Excel"],
        "resume_bullets": ["Unused draft bullet."],
    }


def professional_summary_output(summary: str = "AI summary.") -> dict:
    """Return a professional summary output fixture."""
    return {
        "summary": summary,
        "experience_bullets": [],
        "skills": {"technical": [], "soft": [], "domain": []},
    }


def experience_bullet_output(
    bullets: list[dict] | None = None,
    mode: str = "deterministic",
) -> dict:
    """Return an experience bullet output fixture."""
    return {
        "status": "success",
        "errors": [],
        "provider": "gemini",
        "mode": mode,
        "ai_output": {
            "summary": "",
            "experience_bullets": bullets
            if bullets is not None
            else [
                {
                    "text": "Coordinated reporting workflows.",
                    "source_evidence_id": "EXP001",
                }
            ],
            "skills": {"technical": [], "soft": [], "domain": []},
        },
    }


def skills_section_output(status: str = "success") -> dict:
    """Return a skills section output fixture."""
    return {
        "status": status,
        "errors": [],
        "skills_section": {
            "technical": ["Microsoft Excel"],
            "soft": ["Leadership"],
            "tools": ["CRM"],
            "domain": ["Operations"],
            "matched_skills": ["Excel"],
            "strongest_skills": ["Reporting"],
        },
    }


def assembled_result(
    draft: dict | None = None,
    summary_output: dict | None = None,
    bullet_output: dict | None = None,
    skills_output: dict | None = None,
) -> dict:
    """Assemble a result from default fixtures unless values are provided."""
    return assemble_resume_output(
        resume_draft() if draft is None else draft,
        professional_summary_output() if summary_output is None else summary_output,
        experience_bullet_output() if bullet_output is None else bullet_output,
        skills_output,
    )


def test_successful_assembly() -> None:
    result = assembled_result()

    assert result["status"] == "success"
    assert result["errors"] == []
    assert result["final_resume"]["professional_summary"] == "AI summary."


def test_output_wrapper_contains_status_errors_final_resume() -> None:
    result = assembled_result()

    assert set(result) == {"status", "errors", "final_resume"}


def test_final_resume_contains_job_title() -> None:
    result = assembled_result()

    assert result["final_resume"]["job_title"] == "Operations Coordinator"


def test_final_resume_contains_professional_summary() -> None:
    result = assembled_result()

    assert result["final_resume"]["professional_summary"] == "AI summary."


def test_final_resume_contains_skills() -> None:
    result = assembled_result()

    assert result["final_resume"]["skills"] == {
        "technical": ["Excel", "Reporting"],
        "soft": [],
        "tools": [],
        "domain": [],
        "matched_skills": ["Excel"],
        "strongest_skills": [],
    }


def test_final_resume_contains_experience_bullets() -> None:
    result = assembled_result()

    assert result["final_resume"]["experience_bullets"] == [
        {
            "text": "Coordinated reporting workflows.",
            "source_evidence_id": "EXP001",
        }
    ]


def test_final_resume_contains_metadata() -> None:
    result = assembled_result()

    assert set(result["final_resume"]["metadata"]) == {
        "assembled_by",
        "version",
        "summary_source",
        "bullet_source",
        "skills_source",
    }


def test_uses_professional_summary_output_summary_first() -> None:
    result = assembled_result()

    assert result["final_resume"]["professional_summary"] == "AI summary."
    assert result["final_resume"]["metadata"]["summary_source"] == "ai_generated"


def test_falls_back_to_resume_draft_professional_summary() -> None:
    result = assembled_result(summary_output=professional_summary_output(""))

    assert result["status"] == "partial"
    assert result["final_resume"]["professional_summary"] == "Draft summary."
    assert result["final_resume"]["metadata"]["summary_source"] == "deterministic_fallback"


def test_empty_summary_from_all_sources_marks_partial() -> None:
    draft = resume_draft()
    draft["professional_summary"] = ""

    result = assembled_result(draft=draft, summary_output=professional_summary_output(""))

    assert result["status"] == "partial"
    assert result["final_resume"]["professional_summary"] == ""
    assert result["final_resume"]["metadata"]["summary_source"] == "empty"
    assert "Professional summary missing from all sources." in result["errors"]


def test_none_professional_summary_output_marks_partial() -> None:
    result = assemble_resume_output(
        resume_draft(),
        None,
        experience_bullet_output(),
    )

    assert result["status"] == "partial"
    assert "Professional summary output is missing." in result["errors"]


def test_failed_professional_summary_output_marks_partial() -> None:
    result = assembled_result(summary_output={"status": "failed"})

    assert result["status"] == "partial"
    assert "Professional summary output failed." in result["errors"]


def test_uses_experience_bullet_output_ai_output_experience_bullets() -> None:
    bullets = [{"text": "Exact bullet.", "source_evidence_id": "EXP777"}]

    result = assembled_result(bullet_output=experience_bullet_output(bullets))

    assert result["final_resume"]["experience_bullets"] == bullets


def test_none_experience_bullet_output_marks_partial() -> None:
    result = assemble_resume_output(
        resume_draft(),
        professional_summary_output(),
        None,
    )

    assert result["status"] == "partial"
    assert result["final_resume"]["experience_bullets"] == []
    assert "Experience bullet output is missing." in result["errors"]


def test_failed_experience_bullet_output_marks_partial() -> None:
    result = assembled_result(bullet_output={"status": "failed"})

    assert result["status"] == "partial"
    assert result["final_resume"]["experience_bullets"] == []
    assert "Experience bullet output failed." in result["errors"]


def test_missing_ai_output_marks_partial() -> None:
    result = assembled_result(bullet_output={"status": "success", "mode": "deterministic"})

    assert result["status"] == "partial"
    assert "Experience bullet ai_output is missing." in result["errors"]


def test_missing_experience_bullets_marks_partial() -> None:
    result = assembled_result(
        bullet_output={
            "status": "success",
            "mode": "deterministic",
            "ai_output": {"summary": "", "skills": {}},
        }
    )

    assert result["status"] == "partial"
    assert "Experience bullets missing; used empty list." in result["errors"]


def test_preserves_source_evidence_id() -> None:
    result = assembled_result(
        bullet_output=experience_bullet_output(
            [{"text": "Exact bullet.", "source_evidence_id": "EXP999"}]
        )
    )

    assert result["final_resume"]["experience_bullets"][0]["source_evidence_id"] == "EXP999"


def test_preserves_bullet_text_exactly() -> None:
    exact_text = "  Coordinated reporting workflows exactly as provided.  "
    result = assembled_result(
        bullet_output=experience_bullet_output(
            [{"text": exact_text, "source_evidence_id": "EXP001"}]
        )
    )

    assert result["final_resume"]["experience_bullets"][0]["text"] == exact_text


def test_uses_resume_draft_key_skills() -> None:
    result = assembled_result()

    assert result["final_resume"]["skills"]["technical"] == ["Excel", "Reporting"]


def test_uses_resume_draft_matched_skills() -> None:
    result = assembled_result()

    assert result["final_resume"]["skills"]["matched_skills"] == ["Excel"]


def test_missing_key_skills_uses_empty_list_and_marks_partial() -> None:
    draft = resume_draft()
    draft.pop("key_skills")

    result = assembled_result(draft=draft)

    assert result["status"] == "partial"
    assert result["final_resume"]["skills"]["technical"] == []
    assert "Resume draft key_skills missing; used empty list." in result["errors"]


def test_missing_matched_skills_uses_empty_list_and_marks_partial() -> None:
    draft = resume_draft()
    draft.pop("matched_skills")

    result = assembled_result(draft=draft)

    assert result["status"] == "partial"
    assert result["final_resume"]["skills"]["matched_skills"] == []
    assert "Resume draft matched_skills missing; used empty list." in result["errors"]


def test_missing_job_title_uses_empty_string_and_marks_partial() -> None:
    draft = resume_draft()
    draft.pop("job_title")

    result = assembled_result(draft=draft)

    assert result["status"] == "partial"
    assert result["final_resume"]["job_title"] == ""
    assert "Resume draft job_title missing; used empty string." in result["errors"]


def test_hard_stop_when_resume_draft_is_none() -> None:
    result = assemble_resume_output(None, professional_summary_output(), experience_bullet_output())

    assert result["status"] == "failed"
    assert result["errors"] == ["Resume draft is missing or empty."]


def test_hard_stop_when_resume_draft_is_empty() -> None:
    result = assemble_resume_output({}, professional_summary_output(), experience_bullet_output())

    assert result["status"] == "failed"
    assert result["errors"] == ["Resume draft is missing or empty."]


def test_does_not_import_forbidden_engine_modules() -> None:
    source = Path("engine/resume_output_assembler.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {
        "engine.professional_summary_generator",
        "engine.experience_bullet_generator",
        "engine.hallucination_checker",
        "engine.prompt_builder",
        "engine.resume_draft_builder",
    }
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert forbidden_imports.isdisjoint(imported_modules)



def test_metadata_includes_assembled_by() -> None:
    result = assembled_result()

    assert result["final_resume"]["metadata"]["assembled_by"] == "resume_output_assembler"


def test_metadata_includes_version() -> None:
    result = assembled_result()

    assert result["final_resume"]["metadata"]["version"] == "v1"


def test_metadata_includes_summary_source() -> None:
    result = assembled_result()

    assert result["final_resume"]["metadata"]["summary_source"] == "ai_generated"


def test_metadata_includes_bullet_source() -> None:
    result = assembled_result()

    assert result["final_resume"]["metadata"]["bullet_source"] == "deterministic_evidence"


def test_success_status_returned_when_no_errors() -> None:
    result = assembled_result()

    assert result["status"] == "success"


def test_partial_status_returned_when_recoverable_errors_exist() -> None:
    result = assemble_resume_output(resume_draft(), None, experience_bullet_output())

    assert result["status"] == "partial"


def test_failed_status_returned_when_hard_stop_occurs() -> None:
    result = assemble_resume_output(None, None, None)

    assert result["status"] == "failed"


def test_output_schema_remains_stable() -> None:
    result = assembled_result()

    assert set(result) == {"status", "errors", "final_resume"}
    assert set(result["final_resume"]) == {
        "job_title",
        "professional_summary",
        "skills",
        "experience_bullets",
        "metadata",
    }


def test_old_three_argument_assembler_call_still_works() -> None:
    result = assemble_resume_output(
        resume_draft(),
        professional_summary_output(),
        experience_bullet_output(),
    )

    assert result["status"] == "success"
    assert result["final_resume"]["skills"]["technical"] == ["Excel", "Reporting"]


def test_assembler_accepts_optional_skills_section_output() -> None:
    result = assembled_result(skills_output=skills_section_output())

    assert result["status"] == "success"


def test_uses_successful_skills_section_output() -> None:
    result = assembled_result(skills_output=skills_section_output())

    assert result["final_resume"]["skills"] == skills_section_output()["skills_section"]
    assert result["final_resume"]["metadata"]["skills_source"] == "skills_section_generator"


def test_uses_partial_skills_section_output_when_section_exists() -> None:
    result = assembled_result(skills_output=skills_section_output("partial"))

    assert result["final_resume"]["skills"] == skills_section_output("partial")["skills_section"]
    assert result["final_resume"]["metadata"]["skills_source"] == "skills_section_generator"


def test_falls_back_when_skills_section_output_is_none() -> None:
    result = assembled_result(skills_output=None)

    assert result["final_resume"]["skills"] == {
        "technical": ["Excel", "Reporting"],
        "soft": [],
        "tools": [],
        "domain": [],
        "matched_skills": ["Excel"],
        "strongest_skills": [],
    }
    assert result["final_resume"]["metadata"]["skills_source"] == "resume_draft_fallback"


def test_falls_back_when_skills_section_output_failed() -> None:
    result = assembled_result(skills_output=skills_section_output("failed"))

    assert result["final_resume"]["skills"]["technical"] == ["Excel", "Reporting"]
    assert result["final_resume"]["metadata"]["skills_source"] == "resume_draft_fallback"


def test_falls_back_when_skills_section_missing_skills_section() -> None:
    result = assembled_result(skills_output={"status": "success", "errors": []})

    assert result["final_resume"]["skills"]["technical"] == ["Excel", "Reporting"]
    assert result["final_resume"]["metadata"]["skills_source"] == "resume_draft_fallback"


def test_final_resume_skills_uses_structured_schema() -> None:
    result = assembled_result()

    assert set(result["final_resume"]["skills"]) == {
        "technical",
        "soft",
        "tools",
        "domain",
        "matched_skills",
        "strongest_skills",
    }


def test_metadata_includes_skills_source() -> None:
    result = assembled_result()

    assert result["final_resume"]["metadata"]["skills_source"] == "resume_draft_fallback"


def test_ai_contract_doc_includes_search_grounding_boundary() -> None:
    contract_text = Path("docs/modules/ai_generation_contract.md").read_text(
        encoding="utf-8"
    )

    assert "Search Grounding Boundary" in contract_text
    assert "Search Grounding applies only to market-context outputs" in contract_text
    assert "Search Grounding is never applied to candidate-data generation" in contract_text
