"""
Test Candidate Profile Text Parser

Purpose:
Unit tests for deterministic extracted CV text parsing.
"""

import json
from pathlib import Path

from engine.candidate_profile_text_parser import (
    extract_experience_skills_from_text,
    parse_candidate_profile_text,
)


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
        "English",
        "Arabic",
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


def test_explicit_languages_section_adds_exact_entries_to_skills() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
LANGUAGES
English: Fluent
Nepali: Native
Hindi: Fluent
"""
    )

    skills = result["candidate_profile"]["skills"]
    assert "English: Fluent" in skills
    assert "Nepali: Native" in skills
    assert "Hindi: Fluent" in skills


def test_language_metadata_is_preserved_without_top_level_languages_key() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
LANGUAGES
English: Fluent
Nepali: Native
Hindi: Fluent
"""
    )

    assert result["metadata"]["sections"]["languages"] == [
        "English: Fluent",
        "Nepali: Native",
        "Hindi: Fluent",
    ]
    assert "languages" not in result["candidate_profile"]


def test_ielts_certification_does_not_invent_english_language_skill() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
CERTIFICATIONS
IELTS Band 7.0
"""
    )

    skills = result["candidate_profile"]["skills"]
    assert "English: Fluent" not in skills
    assert "English" not in skills


def test_experience_mention_does_not_invent_language_skill() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
EXPERIENCE
Delivered English classes and IELTS preparation.
"""
    )

    skills = result["candidate_profile"]["skills"]
    assert "English: Fluent" not in skills
    assert "English" not in skills


def test_bullet_separated_languages_section_splits_safely() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
LANGUAGES
\u2022 English: Fluent \u2022 Nepali: Native \u2022 Hindi: Fluent
"""
    )

    assert result["candidate_profile"]["skills"] == [
        "English: Fluent",
        "Nepali: Native",
        "Hindi: Fluent",
    ]


def test_duplicate_language_entries_are_not_duplicated_in_skills() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
SKILLS
English: Fluent

LANGUAGES
English: Fluent
Nepali: Native
"""
    )

    skills = result["candidate_profile"]["skills"]
    assert skills.count("English: Fluent") == 1
    assert skills.count("Nepali: Native") == 1


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


def test_real_pdf_inline_headings_extracts_name() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL Administrative & Operations Executive Sharjah, UAE | +971-54-123-4567 PROFESSIONAL SUMMARY Operations-focused administrator.
"""
    )

    assert result["status"] == "success"
    assert result["candidate_profile"]["name"] == "Aashutosh Badal"


def test_real_pdf_core_competencies_extracts_skills() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL Administrative & Operations Executive CORE COMPETENCIES
• Operations: Workflow Optimization, Project Coordination, Logistics Management.
• Administration: Documentation control, records management, scheduling & reporting
• Technical: MS Office Suite (Advanced Excel), CRM Tools, Power BI (basic dashboards), data reporting, AI tools for productivity.
• Digital Marketing: Meta Ads, basic SEO, Google Analytics, content creation (Canva, CapCut)
• Soft Skills: Stakeholder Communication, Problem-Solving, Team Leadership, Time Management.
"""
    )

    skills = result["candidate_profile"]["skills"]
    assert "Workflow Optimization" in skills
    assert "Project Coordination" in skills
    assert "Documentation control" in skills
    assert "MS Office Suite (Advanced Excel)" in skills
    assert "CRM Tools" in skills
    assert "Google Analytics" in skills
    assert "Stakeholder Communication" in skills
    assert "Operations:" not in skills


def test_skill_block_using_triangle_bullets_splits_into_separate_skills() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Skills
\u25b8 Operations & workflow coordination \u25b8 Data tracking & advanced Excel \u25b8 High-volume client communication
"""
    )

    assert result["candidate_profile"]["skills"] == [
        "Operations & workflow coordination",
        "Data tracking & advanced Excel",
        "High-volume client communication",
    ]


def test_skill_bullet_splitting_works_without_spaces() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Skills
Operations & workflow coordination\u25b8Data tracking & advanced Excel\u25b8High-volume client communication
"""
    )

    assert result["candidate_profile"]["skills"] == [
        "Operations & workflow coordination",
        "Data tracking & advanced Excel",
        "High-volume client communication",
    ]


def test_observed_triangle_skill_block_splits_without_over_splitting_phrases() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL
Skills
\u25b8 Operations & workflow coordination \u25b8 Data tracking & advanced Excel \u25b8 High-volume client communication \u25b8 Stakeholder & cross-cultural communication \u25b8 Document control & record-keeping \u25b8 Process documentation & reporting \u25b8 Training delivery & curriculum design \u25b8 Project support (Agile / PRINCE2 awareness) \u25b8 Field team logistics & scheduling \u25b8 Business Intelligence \u2014 dashboard basics
"""
    )

    skills = result["candidate_profile"]["skills"]
    assert skills == [
        "Operations & workflow coordination",
        "Data tracking & advanced Excel",
        "High-volume client communication",
        "Stakeholder & cross-cultural communication",
        "Document control & record-keeping",
        "Process documentation & reporting",
        "Training delivery & curriculum design",
        "Project support (Agile / PRINCE2 awareness)",
        "Field team logistics & scheduling",
        "Business Intelligence \u2014 dashboard basics",
    ]
    assert len(skills) > 1
    assert "High-volume client communication" in skills
    assert "Stakeholder & cross-cultural communication" in skills
    assert "Document control & record-keeping" in skills
    assert "Project support (Agile / PRINCE2 awareness)" in skills
    assert "Business Intelligence \u2014 dashboard basics" in skills


def test_parenthetical_comma_skill_phrase_is_not_broken() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Skills
content creation (Canva, CapCut)
"""
    )

    assert result["candidate_profile"]["skills"] == [
        "content creation (Canva, CapCut)"
    ]


def test_semicolon_and_pipe_split_clear_skill_separators() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
Skills
Skill One; Skill Two
Skill Three|Skill Four
"""
    )

    assert result["candidate_profile"]["skills"] == [
        "Skill One",
        "Skill Two",
        "Skill Three",
        "Skill Four",
    ]


def test_bullet_skill_splitting_does_not_invent_or_expand_skills() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL
Skills
\u25b8 Data tracking & advanced Excel \u25b8 Business Intelligence \u2014 dashboard basics \u25b8 Project support (Agile / PRINCE2 awareness)
"""
    )

    skills = result["candidate_profile"]["skills"]
    assert "Data tracking & advanced Excel" in skills
    assert "Business Intelligence \u2014 dashboard basics" in skills
    assert "Project support (Agile / PRINCE2 awareness)" in skills
    assert "MS Office" not in skills
    assert "CRM" not in skills
    assert "Power BI" not in skills
    assert "Agile" not in skills
    assert "PRINCE2" not in skills


def test_experience_extracts_microsoft_office_and_html_css_only_nested() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
EXPERIENCE
Taught Microsoft Office, HTML/CSS fundamentals, and exam technique to students.
"""
    )

    experience_skills = result["candidate_profile"]["experience"][0]["skills"]
    assert "Microsoft Office" in experience_skills
    assert "HTML/CSS" in experience_skills
    assert "Microsoft Office" not in result["candidate_profile"]["skills"]
    assert "HTML/CSS" not in result["candidate_profile"]["skills"]


def test_experience_extracts_digital_marketing_tools_only_nested() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
EXPERIENCE
Supported social media scheduling, keyword research, and basic Meta Ads management.
"""
    )

    experience_skills = result["candidate_profile"]["experience"][0]["skills"]
    assert "social media scheduling" in experience_skills
    assert "keyword research" in experience_skills
    assert "Meta Ads" in experience_skills
    assert "social media scheduling" not in result["candidate_profile"]["skills"]
    assert "keyword research" not in result["candidate_profile"]["skills"]
    assert "Meta Ads" not in result["candidate_profile"]["skills"]


def test_experience_extracts_excel_but_not_negated_crm() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
EXPERIENCE
Managed client databases in Excel; no CRM provided.
"""
    )

    experience_skills = result["candidate_profile"]["experience"][0]["skills"]
    assert "Excel" in experience_skills
    assert "CRM" not in experience_skills


def test_experience_does_not_extract_negated_salesforce() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
EXPERIENCE
Worked without Salesforce access; tracked leads manually.
"""
    )

    assert "Salesforce" not in result["candidate_profile"]["experience"][0]["skills"]


def test_experience_does_not_extract_negated_excel() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
EXPERIENCE
Tracked records manually without Excel access.
"""
    )

    assert "Excel" not in result["candidate_profile"]["experience"][0]["skills"]


def test_experience_advanced_excel_does_not_expand_to_ms_office() -> None:
    result = parse_candidate_profile_text(
        """
Jane Admin
EXPERIENCE
Utilized Advanced Excel for weekly reporting.
"""
    )

    experience_skills = result["candidate_profile"]["experience"][0]["skills"]
    assert "Advanced Excel" in experience_skills
    assert "Microsoft Office" not in experience_skills
    assert "MS Office" not in experience_skills


def test_public_helper_extracts_microsoft_office_and_html_css() -> None:
    result = extract_experience_skills_from_text(
        "Taught Microsoft Office, HTML/CSS fundamentals, and exam technique to students."
    )

    assert "Microsoft Office" in result
    assert "HTML/CSS" in result


def test_public_helper_blocks_negated_crm() -> None:
    result = extract_experience_skills_from_text(
        "Managed client databases in Excel from scratch \u2014 no CRM provided."
    )

    assert "Excel" in result
    assert "CRM" not in result


def test_public_helper_blocks_negated_salesforce() -> None:
    result = extract_experience_skills_from_text(
        "Worked without Salesforce access; tracked leads manually."
    )

    assert "Salesforce" not in result


def test_public_helper_does_not_infer_ms_office_from_advanced_excel() -> None:
    result = extract_experience_skills_from_text(
        "Utilized Advanced Excel for weekly reporting."
    )

    assert "Advanced Excel" in result
    assert "Microsoft Office" not in result
    assert "MS Office" not in result


def test_public_helper_includes_known_skills_only_when_explicitly_present() -> None:
    known_skills = ["Communication", "Scheduling"]
    original_known_skills = list(known_skills)

    result = extract_experience_skills_from_text(
        "Handled scheduling and office coordination.",
        known_skills,
    )

    assert "Scheduling" in result
    assert "Communication" not in result
    assert known_skills == original_known_skills


def test_real_pdf_professional_experience_extracts_entries() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL PROFESSIONAL EXPERIENCE
Business Development Executive | Unique Connect, UAE, DEC 2025-Present
• Represent the StarTrader trading platform.
Academic & Administrative Coordinator | Scholarshare Education, Nepal 2022 – 2025
• Coordinated academic administration and student records.
EDUCATION
Bachelor of Business Administration
"""
    )

    experience = result["candidate_profile"]["experience"]
    assert len(experience) >= 2
    assert all(set(entry) == {"id", "text", "skills"} for entry in experience)
    assert any("Business Development Executive" in entry["text"] for entry in experience)
    assert any("Academic & Administrative Coordinator" in entry["text"] for entry in experience)


def test_real_pdf_certifications_and_leadership_extracts_items() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL CERTIFICATIONS & LEADERSHIP
• AI and Cybersecurity Seminar (2025)
• Leadership and Team Management Seminar (2025)
• Financial Statement Analysis Workshop (2025)
• Grade A Trekking Guide – NATHM College (2020)
LANGUAGES
English: Fluent Nepali: Native Hindi: Fluent
"""
    )

    certifications = result["candidate_profile"]["certifications"]
    assert "AI and Cybersecurity Seminar (2025)" in certifications
    assert "Leadership and Team Management Seminar (2025)" in certifications
    assert "Grade A Trekking Guide – NATHM College (2020)" in certifications


def test_inline_professional_experience_does_not_create_professional_skill() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL CORE COMPETENCIES • Operations: Workflow Optimization, Project Coordination PROFESSIONAL EXPERIENCE
Business Development Executive | Unique Connect, UAE, DEC 2025-Present
• Represent the StarTrader trading platform.
EDUCATION
Bachelor of Business Administration
"""
    )

    assert "PROFESSIONAL" not in result["candidate_profile"]["skills"]
    assert "Professional" not in result["candidate_profile"]["skills"]
    assert "Workflow Optimization" in result["candidate_profile"]["skills"]


def test_certifications_and_leadership_does_not_create_leadership_garbage_item() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL CERTIFICATIONS & LEADERSHIP
• AI and Cybersecurity Seminar (2025)
• Grade A Trekking Guide – NATHM College (2020)
LANGUAGES
English: Fluent
"""
    )

    certifications = result["candidate_profile"]["certifications"]
    assert "& LEADERSHIP" not in certifications
    assert "AI and Cybersecurity Seminar (2025)" in certifications
    assert "Grade A Trekking Guide – NATHM College (2020)" in certifications


def test_real_pdf_layout_does_not_invent_missing_sections() -> None:
    result = parse_candidate_profile_text(
        """
AASHUTOSH BADAL Administrative & Operations Executive PROFESSIONAL SUMMARY Operations-focused administrator.
"""
    )

    assert result["candidate_profile"]["skills"] == []
    assert result["candidate_profile"]["experience"] == []
    assert result["candidate_profile"]["certifications"] == []
    assert "Skills section was not found or contained no items." in result["warnings"]


def test_existing_docx_style_text_still_parses() -> None:
    result = parse_candidate_profile_text(sectioned_admin_cv())

    assert result["status"] == "success"
    assert result["candidate_profile"]["name"] == "Jane Admin"
    assert "Documentation" in result["candidate_profile"]["skills"]
    assert result["candidate_profile"]["experience"]


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
