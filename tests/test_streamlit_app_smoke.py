"""
Test Streamlit App Smoke

Purpose:
Lightweight tests for import-safe demo UI helpers.
"""

from pathlib import Path

import pytest

import app


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
