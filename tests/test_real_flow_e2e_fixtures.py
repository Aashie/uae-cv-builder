"""Real-flow E2E regression fixtures for MVP roles."""

from engine.candidate_profile_text_parser import parse_candidate_profile_text
from engine.job_description_text_parser import parse_job_description_text
from engine.section_evidence_trace import build_section_evidence_trace
from engine.upload_paste_analysis_pipeline import run_upload_paste_analysis


FIXTURES = {
    "admin": {
        "cv_text": """
Aisha Khan
Administrative Assistant | Dubai | aisha.khan@example.com | +971 50 111 2222

CORE COMPETENCIES
- Documentation, Scheduling, Records Management
- MS Office, Customer Communication, Data Entry

PROFESSIONAL EXPERIENCE
Administrative Assistant | Bright Star Office Services, Dubai 2023 - Present
- Maintained office records, prepared reports, and supported daily scheduling.
- Coordinated internal communication with customers and office teams.
Office Coordinator | City Training Center, Dubai 2021 - 2023
- Updated training records and handled front desk documentation.

EDUCATION
Diploma in Business Administration

CERTIFICATIONS
- Office Administration Certificate
""",
        "job_text": """
Job Title:
Administrative Assistant

Responsibilities
Maintain records
Schedule meetings
Prepare reports
Coordinate office communication

Requirements and skills
MS Office
Documentation
Scheduling
Customer service
Office administration
Excel
Attention to detail
Arabic language as a plus
""",
        "expected_candidate_skills": ["Documentation", "Scheduling", "MS Office"],
        "jd_only_skills": ["Arabic language", "Excel", "Office administration"],
        "expected_jd_terms": ["MS Office", "Documentation", "Schedule meetings"],
    },
    "customer_service": {
        "cv_text": """
Omar Hassan
Customer Service Representative | Dubai | omar.hassan@example.com | +971 50 333 4444

CORE COMPETENCIES
- Customer Support, Call Handling, Complaint Resolution
- CRM Tools, Email Communication, Data Entry

PROFESSIONAL EXPERIENCE
Customer Service Representative | Gulf Helpdesk Services, Dubai 2022 - Present
- Handled customer support calls and resolved complaints using CRM Tools.
- Maintained customer records and followed up through email communication.
Front Desk Assistant | Marina Business Center, Dubai 2020 - 2022
- Assisted visitors, answered calls, and updated front desk records.

EDUCATION
Diploma in Customer Service

CERTIFICATIONS
- Customer Care Training Certificate
""",
        "job_text": """
Job Title:
Customer Service Representative

Responsibilities
Handle customer inquiries
Resolve complaints
Maintain CRM records
Follow up by phone and email

Requirements and skills
Customer service
CRM
Communication skills
Problem solving
Call center experience
Zendesk
Salesforce
""",
        "expected_candidate_skills": ["Customer Support", "Complaint Resolution", "CRM Tools"],
        "jd_only_skills": ["Zendesk", "Salesforce", "Call center experience"],
        "expected_jd_terms": ["Customer service", "CRM", "Zendesk"],
    },
    "it_support": {
        "cv_text": """
Ravi Sharma
IT Support Assistant | Dubai | ravi.sharma@example.com | +971 50 555 6666

CORE COMPETENCIES
- IT Support, Hardware Troubleshooting, Software Installation
- LAN Support, Helpdesk Documentation, MS Office

PROFESSIONAL EXPERIENCE
IT Support Assistant | Metro Tech Solutions, Dubai 2022 - Present
- Provided IT Support, installed software, and documented helpdesk requests.
- Troubleshot hardware issues and supported LAN connectivity.
Computer Lab Assistant | SkillPoint Institute, Dubai 2020 - 2022
- Prepared lab computers and supported software setup for students.

EDUCATION
Diploma in Information Technology

CERTIFICATIONS
- Computer Hardware Support Certificate
""",
        "job_text": """
Job Title:
IT Support Assistant

Responsibilities
Troubleshoot hardware and software issues
Support LAN connectivity
Install software
Maintain helpdesk tickets

Requirements and skills
IT support
Windows troubleshooting
LAN
Active Directory
Ticketing system
Hardware support
Software installation
""",
        "expected_candidate_skills": ["IT Support", "Hardware Troubleshooting", "LAN Support"],
        "jd_only_skills": ["Active Directory", "Ticketing system", "Windows troubleshooting"],
        "expected_jd_terms": ["IT support", "LAN", "Active Directory"],
    },
}


def _parse_fixture(cv_text, job_text):
    candidate_result = parse_candidate_profile_text(cv_text)
    job_result = parse_job_description_text(job_text)
    assert candidate_result["status"] == "success"
    assert job_result["status"] == "success"
    return candidate_result, job_result


def _flatten_values(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        flattened = []
        for item in value:
            flattened.extend(_flatten_values(item))
        return flattened
    if isinstance(value, dict):
        flattened = []
        for item in value.values():
            flattened.extend(_flatten_values(item))
        return flattened
    return []


def _skills_as_list(skills):
    if isinstance(skills, list):
        return skills
    if isinstance(skills, dict):
        return _flatten_values(skills)
    return []


def _normalize_text(value):
    return " ".join(str(value).strip().lower().split())


def _assert_candidate_parse_is_meaningful(candidate_result):
    candidate_profile = candidate_result.get("candidate_profile", {})
    assert candidate_profile.get("name", "")
    assert len(_skills_as_list(candidate_profile.get("skills", []))) >= 3
    assert len(candidate_profile.get("experience", [])) >= 1
    for entry in candidate_profile.get("experience", []):
        assert {"id", "text", "skills"} <= set(entry)


def _assert_jd_parse_is_meaningful(job_result):
    job_description = job_result.get("job_description", {})
    assert job_description
    assert job_description.get("required_skills", []) or job_description.get("keywords", [])
    metadata_sections = job_result.get("metadata", {}).get("sections", {})
    assert metadata_sections.get("responsibilities") or job_description.get("responsibilities")


def _assert_no_jd_skill_injection(candidate_profile, jd_only_skills):
    candidate_skills = {
        _normalize_text(skill)
        for skill in _skills_as_list(candidate_profile.get("skills", []))
    }
    for jd_only_skill in jd_only_skills:
        assert _normalize_text(jd_only_skill) not in candidate_skills


def _assert_expected_terms_present(parsed_payload, expected_terms):
    searchable = " | ".join(_flatten_values(parsed_payload)).lower()
    for term in expected_terms:
        assert term.lower() in searchable


def _run_reviewed_pipeline(candidate_result, job_text):
    reviewed_profile = candidate_result["candidate_profile"]
    result = run_upload_paste_analysis(
        cv_text="CV text should not be reparsed when reviewed profile is provided.",
        job_text=job_text,
        reviewed_candidate_profile=reviewed_profile,
    )
    completed_stages = result["metadata"]["completed_stages"]
    assert result["metadata"]["candidate_profile_source"] == "reviewed"
    assert "reviewed_candidate_profile" in completed_stages
    assert "candidate_profile_parse" not in completed_stages
    assert result["candidate_parse_result"]["candidate_profile"] == reviewed_profile
    return result


def _assert_fixture_parses(fixture):
    candidate_result, job_result = _parse_fixture(fixture["cv_text"], fixture["job_text"])
    candidate_profile = candidate_result["candidate_profile"]
    _assert_candidate_parse_is_meaningful(candidate_result)
    _assert_jd_parse_is_meaningful(job_result)
    _assert_expected_terms_present(candidate_profile.get("skills", []), fixture["expected_candidate_skills"])
    _assert_expected_terms_present(job_result, fixture["expected_jd_terms"])
    _assert_no_jd_skill_injection(candidate_profile, fixture["jd_only_skills"])


def _assert_reviewed_pipeline_runs(fixture):
    candidate_result, _job_result = _parse_fixture(fixture["cv_text"], fixture["job_text"])
    result = _run_reviewed_pipeline(candidate_result, fixture["job_text"])
    assert set(result) >= {
        "status",
        "candidate_parse_result",
        "job_parse_result",
        "analysis_result",
        "errors",
        "warnings",
        "metadata",
    }
    assert result["metadata"]["candidate_profile_source"] == "reviewed"
    assert isinstance(result["analysis_result"], dict)
    if result["status"] == "success":
        assert result["analysis_result"]
    elif result["status"] == "failed":
        assert result["errors"]


def test_admin_assistant_fixture_parses_candidate_and_jd():
    _assert_fixture_parses(FIXTURES["admin"])


def test_customer_service_fixture_parses_candidate_and_jd():
    _assert_fixture_parses(FIXTURES["customer_service"])


def test_it_support_fixture_parses_candidate_and_jd():
    _assert_fixture_parses(FIXTURES["it_support"])


def test_admin_assistant_reviewed_pipeline_runs_with_reviewed_profile():
    _assert_reviewed_pipeline_runs(FIXTURES["admin"])


def test_customer_service_reviewed_pipeline_runs_with_reviewed_profile():
    _assert_reviewed_pipeline_runs(FIXTURES["customer_service"])


def test_it_support_reviewed_pipeline_runs_with_reviewed_profile():
    _assert_reviewed_pipeline_runs(FIXTURES["it_support"])


def test_section_evidence_trace_builds_when_final_resume_exists():
    for fixture in FIXTURES.values():
        candidate_result, job_result = _parse_fixture(fixture["cv_text"], fixture["job_text"])
        result = _run_reviewed_pipeline(candidate_result, fixture["job_text"])
        analysis_result = result.get("analysis_result", {})
        assert "status" in result
        if analysis_result.get("final_resume"):
            trace = build_section_evidence_trace(
                analysis_result["final_resume"],
                candidate_result["candidate_profile"],
                job_result["job_description"],
            )
            assert trace["trace_level"] == "section"
            assert trace["per_claim_trace"] is False
            assert trace["section_traces"]
        else:
            assert (
                result.get("errors")
                or analysis_result.get("failed_stage")
                or analysis_result.get("final_resume_validation")
            )


def test_fixtures_do_not_insert_jd_only_skills_into_reviewed_profiles():
    for fixture in FIXTURES.values():
        candidate_result, _job_result = _parse_fixture(fixture["cv_text"], fixture["job_text"])
        candidate_profile = candidate_result["candidate_profile"]
        _assert_no_jd_skill_injection(candidate_profile, fixture["jd_only_skills"])
        result = _run_reviewed_pipeline(candidate_result, fixture["job_text"])
        reviewed_profile = result["candidate_parse_result"]["candidate_profile"]
        _assert_no_jd_skill_injection(reviewed_profile, fixture["jd_only_skills"])
