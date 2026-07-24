"""
Test Streamlit App Smoke

Purpose:
Lightweight tests for import-safe demo UI helpers.
"""

from pathlib import Path

import pytest

import app


class _PreviewTab:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def _capture_resume_preview(monkeypatch, final_resume: dict) -> dict[str, list[str]]:
    calls = {"markdown": [], "write": [], "caption": []}

    def capture_markdown(body: str, unsafe_allow_html: bool = False) -> None:
        calls["markdown"].append(body)

    def capture_write(body) -> None:
        calls["write"].append(str(body))

    def capture_caption(body: str) -> None:
        calls["caption"].append(str(body))

    monkeypatch.setattr(app.st, "tabs", lambda labels: [_PreviewTab() for _ in labels])
    monkeypatch.setattr(app.st, "markdown", capture_markdown)
    monkeypatch.setattr(app.st, "write", capture_write)
    monkeypatch.setattr(app.st, "caption", capture_caption)

    app._render_resume_preview(final_resume)
    return calls


def test_app_exposes_helper_functions() -> None:
    assert hasattr(app, "parse_skill_lines")
    assert hasattr(app, "get_sample_profile")
    assert hasattr(app, "get_default_job_values")


def test_parse_skill_lines_handles_newline_and_comma_separated_skills() -> None:
    skills = app.parse_skill_lines("Excel, Communication\nReporting\n Scheduling ")

    assert skills == ["Excel", "Communication", "Reporting", "Scheduling"]


def test_get_sample_profile_loads_non_empty_sample_data() -> None:
    profile = app.get_sample_profile()

    assert profile["name"] == "Sample Candidate"
    assert profile["skills"]
    assert profile["experience"]


def test_get_sample_profile_returns_profile_with_skills_and_experience() -> None:
    profile = app.get_sample_profile()

    assert profile["skills"]
    assert profile["experience"]
    assert profile["experience"][0]["skills"]


def test_get_default_job_values_loads_job_data() -> None:
    values = app.get_default_job_values()

    assert values["job_title"] == "Administrative Assistant"
    assert isinstance(values["required_skills"], str)
    assert isinstance(values["soft_skills"], str)
    assert values["experience_level"] == "Mid"
    assert values["education"] == "Bachelor's"


def test_get_default_job_values_includes_expected_skill_strings() -> None:
    values = app.get_default_job_values()

    assert "Microsoft Excel" in values["required_skills"]
    assert "Communication" in values["soft_skills"]


def test_build_reviewed_experience_recomputes_nested_skills() -> None:
    result = app._build_reviewed_experience(
        [
            "Taught Microsoft Office, HTML/CSS fundamentals, and exam technique.",
            "Handled scheduling and office coordination.",
            "Managed client databases in Excel; no CRM provided.",
        ],
        [{"id": "exp-7"}, {"id": "exp-8"}, {"id": "exp-9"}],
        ["Scheduling"],
    )

    assert result[0]["skills"] == ["Microsoft Office", "HTML/CSS"]
    assert result[1]["skills"] == ["Scheduling"]
    assert "Excel" in result[2]["skills"]
    assert "CRM" not in result[2]["skills"]


def test_render_tags_separates_badge_html(monkeypatch) -> None:
    markdown_calls = []

    def capture_markdown(body: str, unsafe_allow_html: bool = False) -> None:
        markdown_calls.append((body, unsafe_allow_html))

    monkeypatch.setattr(app.st, "markdown", capture_markdown)
    monkeypatch.setattr(app.st, "caption", lambda message: None)

    app._render_tags("Tools", ["Excel", "Meta Ads"], "gray", "")

    rendered_tags = markdown_calls[1][0]
    assert "</span> <span" in rendered_tags
    assert "ExcelMeta Ads" not in rendered_tags


def test_resume_preview_renders_summary_text_when_present(monkeypatch) -> None:
    calls = _capture_resume_preview(
        monkeypatch,
        {
            "professional_summary": "Evidence-backed sales support summary.",
            "skills": {},
            "experience_bullets": [],
        },
    )

    assert "Evidence-backed sales support summary." in calls["write"]
    assert "No professional summary available." not in calls["caption"]


def test_resume_preview_shows_summary_empty_state_when_empty(monkeypatch) -> None:
    calls = _capture_resume_preview(
        monkeypatch,
        {
            "professional_summary": "   ",
            "skills": {},
            "experience_bullets": [],
        },
    )

    assert "No professional summary available." in calls["caption"]


def test_resume_preview_skips_empty_skill_group_labels(monkeypatch) -> None:
    calls = _capture_resume_preview(
        monkeypatch,
        {
            "professional_summary": "Summary.",
            "skills": {
                "technical": [],
                "soft": [],
                "tools": ["Excel"],
                "domain": ["Microsoft Office"],
            },
            "experience_bullets": [],
        },
    )

    rendered_html = "\n".join(calls["markdown"])
    assert "Technical" not in rendered_html
    assert "Soft Skills" not in rendered_html


def test_resume_preview_renders_only_populated_skill_groups(monkeypatch) -> None:
    calls = _capture_resume_preview(
        monkeypatch,
        {
            "professional_summary": "Summary.",
            "skills": {
                "technical": [],
                "soft": [],
                "tools": ["Excel", "Meta Ads"],
                "domain": ["HTML/CSS"],
            },
            "experience_bullets": [],
        },
    )

    rendered_html = "\n".join(calls["markdown"])
    assert "Tools" in rendered_html
    assert "Excel" in rendered_html
    assert "Meta Ads" in rendered_html
    assert "Domain" in rendered_html
    assert "HTML/CSS" in rendered_html


def test_resume_preview_renders_experience_bullet_text_when_present(monkeypatch) -> None:
    calls = _capture_resume_preview(
        monkeypatch,
        {
            "professional_summary": "Summary.",
            "skills": {},
            "experience_bullets": [
                {"text": "Tracked sales data in Excel.", "source_evidence_id": "EXP001"}
            ],
        },
    )

    assert "- Tracked sales data in Excel." in calls["markdown"]
    assert "No experience highlights available." not in calls["caption"]


def test_resume_preview_shows_experience_empty_state_without_visible_bullets(monkeypatch) -> None:
    calls = _capture_resume_preview(
        monkeypatch,
        {
            "professional_summary": "Summary.",
            "skills": {},
            "experience_bullets": [{"text": "  "}, "", None],
        },
    )

    assert "No experience highlights available." in calls["caption"]


def test_resume_preview_supports_dict_and_string_bullets(monkeypatch) -> None:
    calls = _capture_resume_preview(
        monkeypatch,
        {
            "professional_summary": "Summary.",
            "skills": {},
            "experience_bullets": [
                {"text": "Prepared client reports.", "source_evidence_id": "EXP001"},
                "Maintained social media schedules.",
            ],
        },
    )

    assert "- Prepared client reports." in calls["markdown"]
    assert "- Maintained social media schedules." in calls["markdown"]


def _valid_docx_analysis_result() -> dict:
    return {
        "status": "success",
        "final_resume": {"skills": ["Microsoft Office"]},
        "final_resume_validation": {"is_valid": True, "errors": []},
    }


def _set_docx_gate_session_state(monkeypatch, evidence_trace: dict) -> None:
    monkeypatch.setattr(app, "_is_real_flow_analysis_stale", lambda: False)
    app.st.session_state["upload_pipeline_result"] = {"status": "success"}
    app.st.session_state["analysis_stale"] = False
    app.st.session_state["analysis_completed"] = True
    app.st.session_state["real_flow_evidence_trace"] = evidence_trace


def _supported_evidence_trace() -> dict:
    return {
        "status": "success",
        "section_traces": {
            "job_title": {
                "supported": True,
                "support_level": "derived_from_job_description",
            },
            "skills": {
                "supported": True,
                "support_level": "direct",
                "unsupported_resume_skills": [],
            },
            "professional_summary": {
                "supported": True,
                "support_level": "section_level",
            },
            "experience_bullets": {
                "supported": True,
                "support_level": "section_level",
            },
            "metadata_note": {
                "supported": True,
                "support_level": "not_applicable",
                "warnings": ["This MVP trace shows section-level evidence only."],
            },
        },
    }


def test_real_flow_docx_gate_blocks_unsupported_resume_skills(monkeypatch) -> None:
    evidence_trace = _supported_evidence_trace()
    evidence_trace["section_traces"]["skills"]["unsupported_resume_skills"] = ["CRM software"]
    _set_docx_gate_session_state(monkeypatch, evidence_trace)

    can_download, blockers = app._real_flow_docx_gate(_valid_docx_analysis_result())

    assert can_download is False
    assert any("unsupported skills" in blocker for blocker in blockers)
    assert any("CRM software" in blocker for blocker in blockers)


def test_real_flow_docx_gate_allows_supported_skills_trace(monkeypatch) -> None:
    _set_docx_gate_session_state(monkeypatch, _supported_evidence_trace())

    can_download, blockers = app._real_flow_docx_gate(_valid_docx_analysis_result())

    assert can_download is True
    assert blockers == []


def test_real_flow_docx_gate_does_not_block_only_on_missing_job_title_trace(monkeypatch) -> None:
    evidence_trace = _supported_evidence_trace()
    evidence_trace["section_traces"]["job_title"] = {
        "supported": False,
        "support_level": "missing_evidence",
        "warnings": ["Job title source is missing from parsed job description."],
    }
    _set_docx_gate_session_state(monkeypatch, evidence_trace)

    can_download, blockers = app._real_flow_docx_gate(_valid_docx_analysis_result())

    assert can_download is True
    assert blockers == []


def test_missing_sample_profile_file_raises_clear_error(monkeypatch) -> None:
    missing_path = Path("missing_profile.json")
    monkeypatch.setattr(app, "SAMPLE_PROFILE_PATH", missing_path)

    with pytest.raises(FileNotFoundError, match="Sample profile file not found:"):
        app.load_sample_profile()


def test_missing_sample_job_file_raises_clear_error(monkeypatch) -> None:
    missing_path = Path("missing_job.json")
    monkeypatch.setattr(app, "SAMPLE_JOB_PATH", missing_path)

    with pytest.raises(FileNotFoundError, match="Sample job file not found:"):
        app.load_sample_job_values()
