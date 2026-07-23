import copy

from engine.section_evidence_trace import build_section_evidence_trace


def _valid_final_resume():
    return {
        "job_title": "Administrative Assistant",
        "professional_summary": "Experienced administrator.",
        "skills": ["Documentation"],
        "experience_bullets": ["Prepared reports and maintained records."],
    }


def _valid_candidate_profile():
    return {
        "name": "Aisha Khan",
        "skills": ["Documentation"],
        "experience": [
            {
                "id": "exp-1",
                "text": "Prepared reports and maintained office records.",
                "skills": ["Documentation"],
            }
        ],
        "projects": [],
        "certifications": [],
        "achievements": [],
    }


def test_missing_final_resume_fails():
    result = build_section_evidence_trace({}, _valid_candidate_profile())

    assert result["status"] == "failed"
    assert result["section_traces"] == {}
    assert "final_resume" in " ".join(result["errors"])


def test_missing_candidate_profile_fails():
    result = build_section_evidence_trace(_valid_final_resume(), {})

    assert result["status"] == "failed"
    assert result["section_traces"] == {}
    assert "reviewed_candidate_profile" in " ".join(result["errors"])


def test_job_title_traced_to_job_description():
    result = build_section_evidence_trace(
        _valid_final_resume(),
        _valid_candidate_profile(),
        {"job_title": "Administrative Assistant"},
    )

    trace = result["section_traces"]["job_title"]
    assert trace["supported"] is True
    assert trace["support_level"] == "derived_from_job_description"
    assert "parsed_job_description.job_title" in trace["evidence_sources"]


def test_professional_summary_has_section_level_warning():
    result = build_section_evidence_trace(
        _valid_final_resume(),
        _valid_candidate_profile(),
    )

    trace = result["section_traces"]["professional_summary"]
    assert trace["supported"] is True
    assert trace["support_level"] == "section_level"
    assert any("Section-level trace only" in warning for warning in trace["warnings"])


def test_skills_trace_matches_reviewed_candidate_skills_only():
    candidate_profile = {"skills": ["Documentation"]}
    original_profile = copy.deepcopy(candidate_profile)
    final_resume = {"skills": ["Documentation", "Microsoft Excel"]}
    job_description = {"required_skills": ["Microsoft Excel"]}

    result = build_section_evidence_trace(final_resume, candidate_profile, job_description)

    trace = result["section_traces"]["skills"]
    assert "Documentation" in trace["supported_resume_skills"]
    assert "Microsoft Excel" in trace["unsupported_resume_skills"]
    assert "Microsoft Excel" not in trace["supported_resume_skills"]
    assert candidate_profile == original_profile


def test_skill_flattening_handles_dict_categories():
    final_resume = {
        "skills": {
            "technical": ["Documentation", "Reporting"],
            "soft": ["Communication"],
            "tools": ["Documentation"],
            "domain": ["Office Administration"],
            "matched_skills": ["Reporting"],
            "strongest_skills": ["Communication"],
        }
    }
    candidate_profile = {
        "skills": ["Communication", "Documentation", "Office Administration", "Reporting"]
    }

    result = build_section_evidence_trace(final_resume, candidate_profile)

    trace = result["section_traces"]["skills"]
    assert trace["supported_resume_skills"] == [
        "Office Administration",
        "Reporting",
        "Communication",
        "Documentation",
    ]


def test_nested_microsoft_office_supports_microsoft_office_resume_skill():
    result = build_section_evidence_trace(
        {"skills": ["Microsoft Office"]},
        {
            "skills": [],
            "experience": [{"text": "Prepared reports.", "skills": ["Microsoft Office"]}],
        },
    )

    trace = result["section_traces"]["skills"]
    assert "Microsoft Office" in trace["supported_resume_skills"]
    assert trace["unsupported_resume_skills"] == []
    assert trace["candidate_profile_skills"] == []


def test_nested_microsoft_office_supports_ms_office_resume_skill():
    result = build_section_evidence_trace(
        {"skills": ["MS Office"]},
        {
            "skills": [],
            "experience": [{"text": "Prepared reports.", "skills": ["Microsoft Office"]}],
        },
    )

    trace = result["section_traces"]["skills"]
    assert "MS Office" in trace["supported_resume_skills"]
    assert trace["unsupported_resume_skills"] == []


def test_excel_resume_skill_supported_by_advanced_excel_or_nested_excel():
    profile_with_top_level_excel = {
        "skills": ["Data tracking & advanced Excel"],
        "experience": [],
    }
    result = build_section_evidence_trace({"skills": ["Excel"]}, profile_with_top_level_excel)

    trace = result["section_traces"]["skills"]
    assert "Excel" in trace["supported_resume_skills"]

    profile_with_nested_excel = {
        "skills": [],
        "experience": [{"text": "Tracked data.", "skills": ["Excel"]}],
    }
    nested_result = build_section_evidence_trace({"skills": ["Excel"]}, profile_with_nested_excel)

    nested_trace = nested_result["section_traces"]["skills"]
    assert "Excel" in nested_trace["supported_resume_skills"]
    assert nested_trace["unsupported_resume_skills"] == []


def test_nested_experience_skills_support_exact_resume_skills():
    final_resume = {
        "skills": [
            "HTML/CSS",
            "Meta Ads",
            "Keyword Research",
            "Social Media Scheduling",
        ]
    }
    candidate_profile = {
        "skills": [],
        "experience": [
            {
                "text": "Supported digital marketing campaigns.",
                "skills": [
                    "HTML/CSS",
                    "Meta Ads",
                    "keyword research",
                    "social media scheduling",
                ],
            }
        ],
    }

    result = build_section_evidence_trace(final_resume, candidate_profile)

    trace = result["section_traces"]["skills"]
    assert trace["supported_resume_skills"] == [
        "HTML/CSS",
        "Meta Ads",
        "Keyword Research",
        "Social Media Scheduling",
    ]
    assert trace["unsupported_resume_skills"] == []
    assert "reviewed_candidate_profile.experience.skills" in trace["evidence_sources"]


def test_english_profile_skill_supports_proficiency_in_english_resume_skill():
    result = build_section_evidence_trace(
        {"skills": ["Proficiency In English"]},
        {
            "skills": ["English — Fluent (IELTS Band 7.0)"],
            "experience": [],
        },
    )

    trace = result["section_traces"]["skills"]
    assert "Proficiency In English" in trace["supported_resume_skills"]
    assert trace["unsupported_resume_skills"] == []


def test_crm_software_remains_unsupported_without_explicit_crm_evidence():
    result = build_section_evidence_trace(
        {"skills": ["CRM software"]},
        {
            "skills": ["Data tracking & advanced Excel"],
            "experience": [
                {"text": "Tracked work in client databases.", "skills": ["Excel"]},
                {"text": "No CRM provided.", "skills": ["client databases", "no CRM provided"]},
            ],
        },
    )

    trace = result["section_traces"]["skills"]
    assert trace["supported_resume_skills"] == []
    assert trace["unsupported_resume_skills"] == ["CRM software"]


def test_unsupported_resume_skills_are_reported_clearly():
    final_resume = {
        "skills": [
            "Negotiating techniques",
            "Attractive presentations",
            "Fast learner",
            "Results-driven approach",
        ]
    }
    candidate_profile = {
        "skills": ["Data tracking & advanced Excel"],
        "experience": [{"text": "Tracked sales data.", "skills": ["Excel"]}],
    }

    result = build_section_evidence_trace(final_resume, candidate_profile)

    trace = result["section_traces"]["skills"]
    assert trace["supported_resume_skills"] == []
    assert trace["unsupported_resume_skills"] == final_resume["skills"]
    assert any(
        "Unsupported resume skills found in the final resume" in warning
        for warning in trace["warnings"]
    )


def test_experience_trace_is_section_level_only():
    result = build_section_evidence_trace(
        _valid_final_resume(),
        _valid_candidate_profile(),
    )

    trace = result["section_traces"]["experience_bullets"]
    assert trace["supported"] is True
    assert trace["support_level"] == "section_level"
    assert any("individual experience bullets are not verified" in warning for warning in trace["warnings"])


def test_experience_trace_missing_candidate_experience_warns():
    result = build_section_evidence_trace(
        _valid_final_resume(),
        {"skills": ["Documentation"], "experience": []},
    )

    trace = result["section_traces"]["experience_bullets"]
    assert trace["supported"] is False
    assert trace["support_level"] == "missing_evidence"
    assert any("No reviewed experience evidence exists" in warning for warning in trace["warnings"])


def test_trace_return_shape_is_stable():
    result = build_section_evidence_trace(
        _valid_final_resume(),
        _valid_candidate_profile(),
    )

    assert list(result.keys()) == [
        "status",
        "trace_level",
        "per_claim_trace",
        "section_traces",
        "errors",
        "warnings",
        "metadata",
    ]
    assert result["trace_level"] == "section"
    assert result["per_claim_trace"] is False


def test_missing_optional_candidate_keys_are_safe_defaults():
    result = build_section_evidence_trace(
        {
            "professional_summary": "Experienced administrator.",
            "skills": ["Documentation"],
        },
        {"name": "Aisha Khan", "skills": ["Documentation"]},
    )

    assert result["status"] == "success"
    assert result["section_traces"]


def test_job_description_none_is_safe():
    result = build_section_evidence_trace(
        _valid_final_resume(),
        _valid_candidate_profile(),
        job_description=None,
    )

    trace = result["section_traces"]["job_title"]
    assert result["status"] == "success"
    assert trace["support_level"] == "missing_evidence"


def test_candidate_profile_is_not_mutated():
    candidate_profile = {
        "name": "Aisha Khan",
        "skills": ["Documentation", "Reporting"],
        "experience": [
            {
                "id": "exp-1",
                "text": "Prepared reports and maintained office records.",
                "skills": ["Documentation"],
            }
        ],
        "projects": ["Office filing digitization"],
        "certifications": ["Administrative Support Certificate"],
        "achievements": ["Reduced report turnaround time"],
    }
    original_profile = copy.deepcopy(candidate_profile)

    build_section_evidence_trace(_valid_final_resume(), candidate_profile)

    assert candidate_profile == original_profile
