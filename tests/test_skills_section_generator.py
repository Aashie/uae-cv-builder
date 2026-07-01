"""
Test Skills Section Generator

Purpose:
Unit tests for deterministic skills section generation.
"""

import ast
from pathlib import Path

from engine import skills_section_generator as generator


def resume_draft() -> dict:
    """Return a resume draft fixture."""
    return {
        "key_skills": ["Microsoft Excel", "Leadership"],
        "matched_skills": ["Reporting"],
        "job_title": "Ignored Job Title",
    }


def matcher_output() -> dict:
    """Return a matcher output fixture."""
    return {
        "matched_skills": ["CRM"],
        "missing_skills": ["Python"],
    }


def career_insights() -> dict:
    """Return a career insights fixture."""
    return {
        "strongest_skills": ["Scheduling"],
        "skill_frequency": {"Scheduling": 2},
    }


def test_successful_skills_section_generation() -> None:
    result = generator.generate_skills_section(
        resume_draft(),
        matcher_output(),
        career_insights(),
    )

    assert result["status"] == "success"
    assert result["errors"] == []


def test_output_wrapper_contains_status_errors_skills_section() -> None:
    result = generator.generate_skills_section(resume_draft(), matcher_output(), career_insights())

    assert set(result) == {"status", "errors", "skills_section"}


def test_skills_section_contains_category_fields() -> None:
    result = generator.generate_skills_section(resume_draft(), matcher_output(), career_insights())

    assert {"technical", "soft", "tools", "domain"}.issubset(result["skills_section"])


def test_skills_section_contains_matched_skills() -> None:
    result = generator.generate_skills_section(resume_draft(), matcher_output(), career_insights())

    assert "matched_skills" in result["skills_section"]


def test_skills_section_contains_strongest_skills() -> None:
    result = generator.generate_skills_section(resume_draft(), matcher_output(), career_insights())

    assert "strongest_skills" in result["skills_section"]


def test_collects_skills_from_resume_draft_key_skills() -> None:
    result = generator.generate_skills_section({"key_skills": ["Leadership"]}, {}, {})

    assert "Leadership" in result["skills_section"]["soft"]


def test_collects_skills_from_resume_draft_matched_skills() -> None:
    result = generator.generate_skills_section({"matched_skills": ["Reporting"]}, {}, {})

    assert "Reporting" in result["skills_section"]["technical"]


def test_collects_skills_from_matcher_output_matched_skills() -> None:
    result = generator.generate_skills_section({}, {"matched_skills": ["CRM"]}, {})

    assert "CRM" in result["skills_section"]["tools"]


def test_collects_skills_from_career_insights_strongest_skills() -> None:
    result = generator.generate_skills_section({}, {}, {"strongest_skills": ["Scheduling"]})

    assert "Scheduling" in result["skills_section"]["technical"]


def test_verifies_career_insights_strongest_skills_key() -> None:
    result = generator.generate_skills_section({}, {}, {"strongest_skills": ["Reporting"]})

    assert result["skills_section"]["strongest_skills"] == ["Reporting"]


def test_does_not_invent_missing_job_skills() -> None:
    result = generator.generate_skills_section(
        {},
        {"missing_skills": ["Python"], "matched_skills": ["CRM"]},
        {},
    )

    combined_skills = sum(
        (
            result["skills_section"]["technical"],
            result["skills_section"]["soft"],
            result["skills_section"]["tools"],
            result["skills_section"]["domain"],
        ),
        [],
    )
    assert "Python" not in combined_skills


def test_ignores_unsupported_input_fields() -> None:
    result = generator.generate_skills_section(
        {"job_title": "Python Developer"},
        {"required_skills": ["Python"]},
        {"skill_frequency": {"Python": 1}},
    )

    assert result["status"] == "failed"


def test_ignores_none_values() -> None:
    result = generator.generate_skills_section({"key_skills": [None, "Leadership"]}, {}, {})

    assert result["skills_section"]["soft"] == ["Leadership"]


def test_ignores_empty_strings() -> None:
    result = generator.generate_skills_section({"key_skills": ["", "Leadership"]}, {}, {})

    assert result["skills_section"]["soft"] == ["Leadership"]


def test_ignores_whitespace_only_strings() -> None:
    result = generator.generate_skills_section({"key_skills": ["   ", "Leadership"]}, {}, {})

    assert result["skills_section"]["soft"] == ["Leadership"]


def test_ignores_non_string_values() -> None:
    result = generator.generate_skills_section({"key_skills": [123, "Leadership"]}, {}, {})

    assert result["skills_section"]["soft"] == ["Leadership"]


def test_deduplicates_skills_case_insensitively() -> None:
    result = generator.generate_skills_section(
        {"key_skills": ["python", "Python", "PYTHON"]},
        {},
        {},
    )

    assert result["skills_section"]["domain"] == ["Python"]


def test_preserves_readable_title_case() -> None:
    result = generator.generate_skills_section({"key_skills": ["project management"]}, {}, {})

    assert result["skills_section"]["domain"] == ["Project Management"]


def test_preserves_common_acronyms() -> None:
    result = generator.generate_skills_section({"key_skills": ["sql", "uae", "html"]}, {}, {})

    combined_skills = (
        result["skills_section"]["technical"]
        + result["skills_section"]["tools"]
        + result["skills_section"]["domain"]
    )
    assert "SQL" in combined_skills
    assert "UAE" in combined_skills
    assert "HTML" in combined_skills


def test_categorizes_technical_skills_from_reference_data() -> None:
    result = generator.generate_skills_section({"key_skills": ["Reporting"]}, {}, {})

    assert result["skills_section"]["technical"] == ["Reporting"]


def test_categorizes_soft_skills_from_reference_data() -> None:
    result = generator.generate_skills_section({"key_skills": ["Leadership"]}, {}, {})

    assert result["skills_section"]["soft"] == ["Leadership"]


def test_categorizes_tools_using_inline_tools_keyword_list() -> None:
    result = generator.generate_skills_section({"key_skills": ["Salesforce"]}, {}, {})

    assert result["skills_section"]["tools"] == ["Salesforce"]


def test_categorizes_unknown_skills_as_domain() -> None:
    result = generator.generate_skills_section({"key_skills": ["Stakeholder Mapping"]}, {}, {})

    assert result["skills_section"]["domain"] == ["Stakeholder Mapping"]


def test_matched_skills_retained_separately_from_categories() -> None:
    result = generator.generate_skills_section({"matched_skills": ["Reporting"]}, {}, {})

    assert result["skills_section"]["matched_skills"] == ["Reporting"]


def test_strongest_skills_retained_separately_from_categories() -> None:
    result = generator.generate_skills_section({}, {}, {"strongest_skills": ["Scheduling"]})

    assert result["skills_section"]["strongest_skills"] == ["Scheduling"]


def test_matched_skills_are_not_removed_from_categorized_skills() -> None:
    result = generator.generate_skills_section({"matched_skills": ["Reporting"]}, {}, {})

    assert result["skills_section"]["matched_skills"] == ["Reporting"]
    assert "Reporting" in result["skills_section"]["technical"]


def test_strongest_skills_are_not_removed_from_categorized_skills() -> None:
    result = generator.generate_skills_section({}, {}, {"strongest_skills": ["Scheduling"]})

    assert result["skills_section"]["strongest_skills"] == ["Scheduling"]
    assert "Scheduling" in result["skills_section"]["technical"]


def test_no_skills_found_returns_failed_status() -> None:
    result = generator.generate_skills_section({}, {}, {})

    assert result == {
        "status": "failed",
        "errors": ["No skills found. Cannot generate skills section."],
        "skills_section": {
            "technical": [],
            "soft": [],
            "tools": [],
            "domain": [],
            "matched_skills": [],
            "strongest_skills": [],
        },
    }


def test_none_inputs_return_failed_if_no_skills_found() -> None:
    result = generator.generate_skills_section(None, None, None)

    assert result["status"] == "failed"


def test_missing_one_input_can_still_succeed_if_other_sources_contain_skills() -> None:
    result = generator.generate_skills_section(None, {"matched_skills": ["CRM"]}, None)

    assert result["status"] == "success"
    assert "CRM" in result["skills_section"]["tools"]


def test_technical_reference_loading_failure_returns_partial(monkeypatch) -> None:
    def fake_loader(filename: str):
        if filename == "skills.json":
            raise FileNotFoundError
        return ["leadership"]

    monkeypatch.setattr(generator, "load_reference_data", fake_loader)

    result = generator.generate_skills_section({"key_skills": ["Reporting"]}, {}, {})

    assert result["status"] == "partial"
    assert "Technical skills reference data could not be loaded." in result["errors"]


def test_soft_reference_loading_failure_returns_partial(monkeypatch) -> None:
    def fake_loader(filename: str):
        if filename == "soft_skills.json":
            raise FileNotFoundError
        return ["reporting"]

    monkeypatch.setattr(generator, "load_reference_data", fake_loader)

    result = generator.generate_skills_section({"key_skills": ["Leadership"]}, {}, {})

    assert result["status"] == "partial"
    assert "Soft skills reference data could not be loaded." in result["errors"]


def test_reference_loading_failure_falls_back_safely(monkeypatch) -> None:
    monkeypatch.setattr(
        generator,
        "load_reference_data",
        lambda filename: (_ for _ in ()).throw(FileNotFoundError),
    )

    result = generator.generate_skills_section({"key_skills": ["Leadership"]}, {}, {})

    assert result["status"] == "partial"
    assert result["skills_section"]["domain"] == ["Leadership"]


def test_no_gemini_or_api_call_required() -> None:
    result = generator.generate_skills_section({"key_skills": ["Leadership"]}, {}, {})

    assert result["status"] == "success"


def test_no_orchestrator_modification_required() -> None:
    source_path = Path("engine") / "skills_section_generator.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))

    forbidden_imports = {"engine.resume_analysis_orchestrator"}
    imported_modules = set()

    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert imported_modules.isdisjoint(forbidden_imports)


def test_stable_output_schema() -> None:
    result = generator.generate_skills_section(resume_draft(), matcher_output(), career_insights())

    assert set(result) == {"status", "errors", "skills_section"}
    assert set(result["skills_section"]) == {
        "technical",
        "soft",
        "tools",
        "domain",
        "matched_skills",
        "strongest_skills",
    }
