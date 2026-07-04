"""
Test Job Description Text Parser

Purpose:
Unit tests for deterministic pasted job description parsing.
"""

from dataclasses import fields

from models.job_description import JobDescription
from engine.job_description_text_parser import parse_job_description_text


def sectioned_admin_jd() -> str:
    """Return a sectioned admin/operations JD fixture."""
    return """
Job Title:
Administrative Assistant

Responsibilities
- Coordinate office documentation
- Maintain administrative reports

Required Skills
- Documentation
- Microsoft Excel
- Communication
- Scheduling

Requirements
- Administrative support experience
- Strong records management knowledge

Experience
Mid level administrative experience

Education
Bachelor's degree
"""


def test_valid_sectioned_admin_jd_parses_job_description_payload() -> None:
    result = parse_job_description_text(sectioned_admin_jd())

    assert result["status"] == "success"
    assert result["errors"] == []
    assert result["job_description"]["job_title"] == "Administrative Assistant"
    assert result["job_description"]["required_skills"] == [
        "Documentation",
        "Microsoft Excel",
        "Communication",
        "Scheduling",
    ]
    assert result["job_description"]["experience_level"] == (
        "Mid level administrative experience"
    )
    assert result["job_description"]["education"] == "Bachelor's degree"


def test_job_description_contains_same_top_level_keys_as_model() -> None:
    result = parse_job_description_text(sectioned_admin_jd())

    assert list(result["job_description"]) == [
        field.name for field in fields(JobDescription)
    ]


def test_responsibilities_extraction() -> None:
    result = parse_job_description_text(sectioned_admin_jd())

    assert result["metadata"]["sections"]["responsibilities"] == [
        "Coordinate office documentation",
        "Maintain administrative reports",
    ]


def test_required_skills_extraction() -> None:
    result = parse_job_description_text(sectioned_admin_jd())

    assert "Microsoft Excel" in result["job_description"]["required_skills"]
    assert "Communication" in result["job_description"]["required_skills"]
    assert result["job_description"]["soft_skills"] == ["Communication"]


def test_preferred_skills_are_not_included_in_required_skills() -> None:
    text = """
Job Title: Operations Coordinator

Required Skills
- Documentation

Preferred Skills
- Power BI
- Arabic language
"""

    result = parse_job_description_text(text)

    assert result["job_description"]["required_skills"] == ["Documentation"]
    assert "Power BI" not in result["job_description"]["required_skills"]
    assert "Arabic language" not in result["job_description"]["required_skills"]
    assert result["metadata"]["sections"]["preferred_skills"] == [
        "Power BI",
        "Arabic language",
    ]


def test_requirements_and_qualifications_extraction() -> None:
    text = """
Job Title: Operations Coordinator

Qualifications
- UAE office administration experience
- Certified Administrative Professional certification
"""

    result = parse_job_description_text(text)

    assert result["job_description"]["keywords"] == [
        "UAE office administration experience",
        "Certified Administrative Professional certification",
    ]
    assert result["job_description"]["certifications"] == [
        "Certified Administrative Professional certification"
    ]


def test_missing_sections_produce_warnings() -> None:
    result = parse_job_description_text("Job Title: Office Assistant")

    assert result["status"] == "success"
    assert "Responsibilities section was not found." in result["warnings"]
    assert (
        "Required skills section was not found or contained no items."
        in result["warnings"]
    )
    assert "Education section was not found." in result["warnings"]


def test_messy_heading_capitalization_still_parses() -> None:
    text = """
job title:
Admin Assistant

rEqUiReD sKiLlS:
* Documentation
* Reporting

eDuCaTiOn:
Diploma
"""

    result = parse_job_description_text(text)

    assert result["job_description"]["job_title"] == "Admin Assistant"
    assert result["job_description"]["required_skills"] == [
        "Documentation",
        "Reporting",
    ]
    assert result["job_description"]["education"] == "Diploma"


def test_bullet_formats_using_hyphen_asterisk_and_numbered_lines() -> None:
    text = """
Job Title: Admin Assistant

Responsibilities
- Prepare reports
* Maintain calendars
1. Coordinate meetings
2) Update trackers
"""

    result = parse_job_description_text(text)

    assert result["metadata"]["sections"]["responsibilities"] == [
        "Prepare reports",
        "Maintain calendars",
        "Coordinate meetings",
        "Update trackers",
    ]


def test_ambiguous_heading_words_inside_sentences_are_not_section_headings() -> None:
    text = """
Job Title: Admin Assistant
The responsibilities include reporting and scheduling in a busy office.
The skills required include Microsoft Excel but this sentence is not a heading.
"""

    result = parse_job_description_text(text)

    assert result["metadata"]["sections"]["responsibilities"] == []
    assert result["job_description"]["required_skills"] == []
    assert "Microsoft Excel" not in result["job_description"]["required_skills"]


def test_empty_string_returns_failed_result() -> None:
    result = parse_job_description_text("")

    assert result["status"] == "failed"
    assert result["errors"] == ["job_text must be a non-empty string."]


def test_whitespace_only_string_returns_failed_result() -> None:
    result = parse_job_description_text(" \n\t ")

    assert result["status"] == "failed"
    assert result["errors"] == ["job_text must be a non-empty string."]


def test_non_string_input_returns_failed_result() -> None:
    result = parse_job_description_text([])

    assert result["status"] == "failed"
    assert result["errors"] == ["job_text must be a string."]


def test_parser_does_not_invent_skills_not_present_in_jd_text() -> None:
    result = parse_job_description_text(
        """
Job Title: Office Assistant

Required Skills
- Documentation
"""
    )

    assert result["job_description"]["required_skills"] == ["Documentation"]
    assert "Microsoft Excel" not in result["job_description"]["required_skills"]
    assert "Leadership" not in result["job_description"]["required_skills"]


def test_return_shape_is_exact() -> None:
    result = parse_job_description_text(sectioned_admin_jd())

    assert set(result) == {
        "status",
        "job_description",
        "errors",
        "warnings",
        "metadata",
    }


def test_metadata_contains_parser_name_version_and_source() -> None:
    result = parse_job_description_text(sectioned_admin_jd())

    assert result["metadata"]["parser"] == "job_description_text_parser"
    assert result["metadata"]["version"] == "v1"
    assert result["metadata"]["source"] == "pasted_job_description"
