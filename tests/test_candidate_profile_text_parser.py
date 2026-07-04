"""
Test Candidate Profile Text Parser

Purpose:
Unit tests for deterministic extracted CV text parsing.
"""

import json
from pathlib import Path

from engine.candidate_profile_text_parser import parse_candidate_profile_text


SAMPLE_PROFILE_PATH = Path("samples/sample_profile_admin.json")


def sample_profile_keys() -> list[str]:
    """Return top-level keys from the sample candidate profile."""
    return list(json.loads(SAMPLE_PROFILE_PATH.read_text(encoding="utf-8")))


def sectioned_admin_cv() -> str:
    """Return a sectioned admin/operations CV fixture."""
    return """
Jane Admin
Contact
jane.admin@example.com
+971 50 123 4567

Summary
Administrative assistant focused on office support.

Skills
- Documentation
- Microsoft Excel
- Communication
- Scheduling

Work Experience
- Coordinated office documentation and used Microsoft Excel trackers.
- Prepared administrative reports.

Education
- Bachelor of Business Administration

Certifications
- Certified Administrative Professional

Projects
- Office filing improvement project

Languages
- English
- Arabic
"""


def test_valid_sectioned_admin_cv_parses_candidate_profile_payload() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["status"] == "success"
    assert result["errors"] == []
    assert result["candidate_profile"]["name"] == "Jane Admin"
    assert result["candidate_profile"]["skills"] == [
        "Documentation",
        "Microsoft Excel",
        "Communication",
        "Scheduling",
    ]
    assert result["candidate_profile"]["certifications"] == [
        "Certified Administrative Professional"
    ]
    assert result["candidate_profile"]["projects"] == [
        "Office filing improvement project"
    ]


def test_candidate_profile_contains_same_top_level_keys_as_sample_profile() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert list(result["candidate_profile"]) == sample_profile_keys()


def test_name_email_and_phone_extraction_when_clearly_present() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["candidate_profile"]["name"] == "Jane Admin"
    assert result["metadata"]["contact"]["email"] == "jane.admin@example.com"
    assert result["metadata"]["contact"]["phone"] == "+971 50 123 4567"


def test_valid_name_extraction_still_works() -> None:
    result = parse_candidate_profile_text("Jane Admin\nSkills\n- Documentation")

    assert result["candidate_profile"]["name"] == "Jane Admin"


def test_first_line_summary_is_not_extracted_as_candidate_name() -> None:
    result = parse_candidate_profile_text(
        """
SUMMARY
Administrative assistant with office support experience.
"""
    )

    assert result["candidate_profile"]["name"] == ""
    assert "Candidate name was not found in the first meaningful CV line." in result["warnings"]


def test_first_line_resume_is_not_extracted_as_candidate_name() -> None:
    result = parse_candidate_profile_text(
        """
RESUME
Jane Admin
"""
    )

    assert result["candidate_profile"]["name"] == ""
    assert "Candidate name was not found in the first meaningful CV line." in result["warnings"]


def test_first_line_curriculum_vitae_is_not_extracted_as_candidate_name() -> None:
    result = parse_candidate_profile_text(
        """
CURRICULUM VITAE
Jane Admin
"""
    )

    assert result["candidate_profile"]["name"] == ""


def test_first_line_email_is_not_extracted_as_candidate_name() -> None:
    result = parse_candidate_profile_text(
        """
jane.admin@example.com
Jane Admin
"""
    )

    assert result["candidate_profile"]["name"] == ""
    assert result["metadata"]["contact"]["email"] == "jane.admin@example.com"


def test_first_line_uae_phone_is_not_extracted_as_candidate_name() -> None:
    result = parse_candidate_profile_text(
        """
+971 50 123 4567
Jane Admin
"""
    )

    assert result["candidate_profile"]["name"] == ""
    assert result["metadata"]["contact"]["phone"] == "+971 50 123 4567"


def test_first_line_linkedin_url_is_not_extracted_as_candidate_name() -> None:
    result = parse_candidate_profile_text(
        """
linkedin.com/in/jane-admin
Jane Admin
"""
    )

    assert result["candidate_profile"]["name"] == ""


def test_email_regex_does_not_match_missing_tld() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Contact
test@example
"""
    )

    assert result["metadata"]["contact"]["email"] == ""


def test_phone_regex_does_not_match_date_ranges() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Professional Experience
2019-2023 Office Assistant
"""
    )

    assert result["metadata"]["contact"]["phone"] == ""


def test_skills_extraction_from_explicit_skills_section() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Skills
- Documentation
* Reporting
1. Scheduling
"""
    )

    assert result["candidate_profile"]["skills"] == [
        "Documentation",
        "Reporting",
        "Scheduling",
    ]


def test_tools_and_technical_skills_extract_to_supported_skills_shape() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Technical Skills
- Microsoft Excel
Tools
- CRM
"""
    )

    assert result["candidate_profile"]["skills"] == ["Microsoft Excel", "CRM"]


def test_parser_does_not_invent_skills_from_experience_education_or_projects() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Professional Experience
- Used Microsoft Excel for reporting.
Education
- Bachelor of Business Administration
Projects
- CRM cleanup project
"""
    )

    assert result["candidate_profile"]["skills"] == []


def test_work_experience_extraction_from_explicit_experience_section() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["candidate_profile"]["experience"][0]["text"] == (
        "Coordinated office documentation and used Microsoft Excel trackers."
    )
    assert result["candidate_profile"]["experience"][1]["text"] == (
        "Prepared administrative reports."
    )


def test_experience_entries_have_sample_shape() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["candidate_profile"]["experience"][0] == {
        "id": "exp-1",
        "text": "Coordinated office documentation and used Microsoft Excel trackers.",
        "skills": ["Documentation", "Microsoft Excel"],
    }


def test_education_extraction_from_explicit_education_section() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["metadata"]["sections"]["education"] == [
        "Bachelor of Business Administration"
    ]


def test_certifications_extraction_from_explicit_certifications_section() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["candidate_profile"]["certifications"] == [
        "Certified Administrative Professional"
    ]


def test_languages_extraction_when_supported_in_metadata() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["metadata"]["sections"]["languages"] == ["English", "Arabic"]


def test_missing_sections_produce_warnings() -> None:
    result = parse_candidate_profile_text("Jane Admin")

    assert "Skills section was not found or contained no items." in result["warnings"]
    assert "Experience section was not found or contained no items." in result["warnings"]
    assert "Education section was not found or contained no items." in result["warnings"]


def test_messy_heading_capitalization_still_parses() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
sKiLlS:
* Documentation
pRoFeSsIoNaL eXpErIeNcE:
* Prepared reports
"""
    )

    assert result["candidate_profile"]["skills"] == ["Documentation"]
    assert result["candidate_profile"]["experience"][0]["text"] == "Prepared reports"


def test_bullet_formats_using_hyphen_asterisk_and_numbered_lines() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Skills
- Documentation
* Reporting
1. Scheduling
2) Communication
"""
    )

    assert result["candidate_profile"]["skills"] == [
        "Documentation",
        "Reporting",
        "Scheduling",
        "Communication",
    ]


def test_bullet_character_is_stripped_in_skills_and_experience_sections() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Skills
• Documentation
Professional Experience
• Prepared reports
"""
    )

    assert result["candidate_profile"]["skills"] == ["Documentation"]
    assert result["candidate_profile"]["experience"][0]["text"] == "Prepared reports"


def test_ambiguous_heading_words_inside_sentences_are_not_section_headings() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
My skills include Microsoft Excel, but this is not a heading.
My experience includes office coordination, but this is not a heading.
"""
    )

    assert result["candidate_profile"]["skills"] == []
    assert result["candidate_profile"]["experience"] == []


def test_empty_string_returns_failed_result() -> None:
    result = parse_candidate_profile_text("")

    assert result["status"] == "failed"
    assert result["errors"] == ["cv_text must be a non-empty string."]


def test_whitespace_only_string_returns_failed_result() -> None:
    result = parse_candidate_profile_text(" \n\t ")

    assert result["status"] == "failed"
    assert result["errors"] == ["cv_text must be a non-empty string."]


def test_non_string_input_returns_failed_result() -> None:
    result = parse_candidate_profile_text([])

    assert result["status"] == "failed"
    assert result["errors"] == ["cv_text must be a string."]


def test_parser_does_not_invent_experience_years_companies_certifications_or_degrees() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Skills
- Documentation
Professional Experience
- Prepared reports.
"""
    )

    assert result["candidate_profile"]["experience"][0]["text"] == "Prepared reports."
    assert result["candidate_profile"]["certifications"] == []
    assert result["metadata"]["sections"]["education"] == []
    assert "2019" not in result["candidate_profile"]["experience"][0]["text"]
    assert "Certified Administrative Professional" not in result["candidate_profile"]["certifications"]


def test_return_shape_is_exact() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert set(result) == {
        "status",
        "candidate_profile",
        "errors",
        "warnings",
        "metadata",
    }


def test_metadata_contains_parser_name_version_and_source() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["metadata"]["parser"] == "candidate_profile_text_parser"
    assert result["metadata"]["version"] == "v1"
    assert result["metadata"]["source"] == "extracted_cv_text"
