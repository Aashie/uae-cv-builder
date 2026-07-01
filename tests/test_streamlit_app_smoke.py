"""
Test Streamlit App Smoke

Purpose:
Lightweight tests for import-safe demo UI helpers.
"""

import app


def test_app_exposes_helper_functions() -> None:
    assert hasattr(app, "parse_skill_lines")
    assert hasattr(app, "get_sample_profile")
    assert hasattr(app, "get_default_job_values")


def test_parse_skill_lines_handles_newline_and_comma_separated_skills() -> None:
    skills = app.parse_skill_lines("Excel, Communication\nReporting\n Scheduling ")

    assert skills == ["Excel", "Communication", "Reporting", "Scheduling"]


def test_get_sample_profile_returns_non_empty_profile() -> None:
    profile = app.get_sample_profile()

    assert profile["skills"]
    assert profile["experience"]
    assert profile["experience"][0]["skills"]


def test_get_default_job_values_returns_required_fields() -> None:
    values = app.get_default_job_values()

    assert values["job_title"]
    assert values["required_skills"]
    assert values["experience_level"]
    assert values["education"]
