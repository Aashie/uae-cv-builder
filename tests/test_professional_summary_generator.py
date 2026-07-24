"""
Test Professional Summary Generator

Purpose:
Unit tests for provider-dispatched professional summary generation.
"""

import pytest

from engine import professional_summary_generator as generator


def resume_draft(summary: str = "Experienced operations professional.") -> dict:
    """Return a resume draft fixture."""
    return {
        "professional_summary": summary,
        "key_skills": ["Excel"],
        "matched_skills": ["Microsoft Office"],
    }


def prompt_package() -> dict:
    """Return a prompt package fixture."""
    return {
        "job_title": "Operations Coordinator",
        "strongest_skills": ["Excel"],
        "matched_skills": ["Microsoft Office"],
        "critical_gaps": ["CRM"],
    }


def valid_ai_response(summary: str = "Generated professional summary.") -> dict:
    """Return a valid V1 AI output fixture."""
    return {
        "summary": summary,
        "experience_bullets": [],
        "skills": {
            "technical": [],
            "soft": [],
            "domain": [],
        },
    }


def test_gemini_provider_path(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def fake_gemini(prompt: dict, draft: dict) -> dict:
        calls.append((prompt, draft))
        return valid_ai_response()

    monkeypatch.setattr(generator, "_generate_with_gemini", fake_gemini)

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft(),
        provider="gemini",
    )

    assert result["summary"] == "Generated professional summary."
    assert len(calls) == 1


def test_unsupported_provider_raises_value_error() -> None:
    with pytest.raises(ValueError):
        generator.generate_professional_summary({}, {}, provider="unsupported")


def test_valid_ai_response_returns_full_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        generator,
        "_generate_with_gemini",
        lambda prompt, draft: valid_ai_response("Valid summary."),
    )

    result = generator.generate_professional_summary(prompt_package(), resume_draft())

    assert result == valid_ai_response("Valid summary.")


def test_invalid_response_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generator, "_generate_with_gemini", lambda prompt, draft: [])
    monkeypatch.setattr(generator, "_retry_delay", lambda: None)

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Fallback summary."),
    )

    assert result == valid_ai_response(
        "Professional profile includes reviewed skills in Excel. "
        "Supported matched strengths include Microsoft Office."
    )


def test_missing_summary_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        generator,
        "_generate_with_gemini",
        lambda prompt, draft: {"experience_bullets": [], "skills": generator._empty_skills()},
    )
    monkeypatch.setattr(generator, "_retry_delay", lambda: None)

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Fallback summary."),
    )

    assert result["summary"] == (
        "Professional profile includes reviewed skills in Excel. "
        "Supported matched strengths include Microsoft Office."
    )


def test_empty_response_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generator, "_generate_with_gemini", lambda prompt, draft: {})
    monkeypatch.setattr(generator, "_retry_delay", lambda: None)

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Fallback summary."),
    )

    assert result == valid_ai_response(
        "Professional profile includes reviewed skills in Excel. "
        "Supported matched strengths include Microsoft Office."
    )


def test_experience_bullets_remains_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        generator,
        "_generate_with_gemini",
        lambda prompt, draft: valid_ai_response(),
    )

    result = generator.generate_professional_summary(prompt_package(), resume_draft())

    assert result["experience_bullets"] == []


def test_skills_remain_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        generator,
        "_generate_with_gemini",
        lambda prompt, draft: valid_ai_response(),
    )

    result = generator.generate_professional_summary(prompt_package(), resume_draft())

    assert result["skills"] == {"technical": [], "soft": [], "domain": []}


def test_fallback_uses_resume_draft_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generator, "_generate_with_gemini", lambda prompt, draft: None)
    monkeypatch.setattr(generator, "_retry_delay", lambda: None)

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Resume draft summary."),
    )

    assert result["summary"] == (
        "Professional profile includes reviewed skills in Excel. "
        "Supported matched strengths include Microsoft Office."
    )


def test_fallback_uses_empty_summary_when_resume_draft_summary_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(generator, "_generate_with_gemini", lambda prompt, draft: None)
    monkeypatch.setattr(generator, "_retry_delay", lambda: None)

    result = generator.generate_professional_summary(prompt_package(), {})

    assert result["summary"] == (
        "Professional profile requires reviewed candidate evidence before "
        "a tailored summary can be generated."
    )


def test_invalid_response_retries_once(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = [
        {"summary": "", "experience_bullets": [], "skills": generator._empty_skills()},
        valid_ai_response("Retry summary."),
    ]
    delay_calls = []

    def fake_gemini(prompt: dict, draft: dict) -> dict:
        return responses.pop(0)

    monkeypatch.setattr(generator, "_generate_with_gemini", fake_gemini)
    monkeypatch.setattr(generator, "_retry_delay", lambda: delay_calls.append("delay"))

    result = generator.generate_professional_summary(prompt_package(), resume_draft())

    assert result["summary"] == "Retry summary."
    assert delay_calls == ["delay"]


def test_timeout_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def fake_gemini(prompt: dict, draft: dict) -> dict:
        calls.append("call")
        raise generator.ProviderTimeoutError

    monkeypatch.setattr(generator, "_generate_with_gemini", fake_gemini)

    result = generator.generate_professional_summary(prompt_package(), resume_draft())

    assert result["summary"] == (
        "Professional profile includes reviewed skills in Excel. "
        "Supported matched strengths include Microsoft Office."
    )
    assert calls == ["call"]


def test_authentication_failure_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def fake_gemini(prompt: dict, draft: dict) -> dict:
        calls.append("call")
        raise generator.ProviderAuthenticationError

    monkeypatch.setattr(generator, "_generate_with_gemini", fake_gemini)

    result = generator.generate_professional_summary(prompt_package(), resume_draft())

    assert result["summary"] == (
        "Professional profile includes reviewed skills in Excel. "
        "Supported matched strengths include Microsoft Office."
    )
    assert calls == ["call"]


def test_rate_limit_error_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def fake_gemini(prompt: dict, draft: dict) -> dict:
        calls.append("call")
        raise generator.ProviderRateLimitError

    monkeypatch.setattr(generator, "_generate_with_gemini", fake_gemini)

    result = generator.generate_professional_summary(prompt_package(), resume_draft())

    assert result["summary"] == (
        "Professional profile includes reviewed skills in Excel. "
        "Supported matched strengths include Microsoft Office."
    )
    assert calls == ["call"]


def test_no_real_gemini_api_call_required() -> None:
    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Deterministic placeholder summary."),
    )

    assert result == valid_ai_response(
        "Professional targeting Operations Coordinator roles with reviewed skills in Excel. "
        "Supported matched strengths include Microsoft Office."
    )


def test_generated_summary_does_not_contain_match_score_or_opportunities() -> None:
    result = generator.generate_professional_summary(
        {
            "job_title": "",
            "match_score": 28.57,
            "strongest_skills": ["Excel"],
            "matched_skills": ["Microsoft Office"],
        },
        {
            "professional_summary": "Professional with a 28.57% match score for  opportunities.",
            "key_skills": ["Excel"],
            "matched_skills": ["Microsoft Office"],
        },
    )

    summary = result["summary"]
    assert "match score" not in summary
    assert "28.57%" not in summary
    assert "for opportunities" not in summary
    assert "for  opportunities" not in summary


def test_missing_jd_title_uses_role_neutral_summary() -> None:
    result = generator.generate_professional_summary(
        {"job_title": "", "strongest_skills": ["Excel"]},
        {"key_skills": ["Excel"], "matched_skills": []},
    )

    assert result["summary"] == "Professional profile includes reviewed skills in Excel."
    assert "targeting" not in result["summary"]


def test_summary_does_not_use_missing_skills_or_missing_crm() -> None:
    result = generator.generate_professional_summary(
        {
            "job_title": "",
            "strongest_skills": ["Excel"],
            "matched_skills": ["Microsoft Office"],
            "missing_skills": ["CRM"],
            "critical_gaps": ["CRM"],
        },
        {"key_skills": ["Excel"], "matched_skills": ["Microsoft Office"]},
    )

    assert "CRM" not in result["summary"]
    assert "Microsoft Office" in result["summary"]


def test_html_css_display_label_is_normalized_in_summary() -> None:
    mixed_case_result = generator.generate_professional_summary(
        {"strongest_skills": ["Html/Css"]},
        {"key_skills": ["Html/Css"], "matched_skills": []},
    )
    lower_case_result = generator.generate_professional_summary(
        {"strongest_skills": ["html/css"]},
        {"key_skills": ["html/css"], "matched_skills": []},
    )

    assert "HTML/CSS" in mixed_case_result["summary"]
    assert "Html/Css" not in mixed_case_result["summary"]
    assert "HTML/CSS" in lower_case_result["summary"]
    assert "html/css" not in lower_case_result["summary"]


def test_jd_ms_office_phrase_maps_to_safe_microsoft_office_label() -> None:
    result = generator.generate_professional_summary(
        {"matched_skills": ["Excellent knowledge of MS Office"]},
        {"key_skills": ["Excel"], "matched_skills": ["Excellent knowledge of MS Office"]},
    )

    assert "Microsoft Office" in result["summary"]
    assert "Excellent knowledge" not in result["summary"]
    assert "Excellent knowledge of MS Office" not in result["summary"]


def test_microsoft_office_only_appears_when_supported() -> None:
    unsupported_result = generator.generate_professional_summary(
        {"matched_skills": [], "strongest_skills": ["Excel"]},
        {"key_skills": ["Excel"], "matched_skills": []},
    )
    supported_result = generator.generate_professional_summary(
        {"matched_skills": ["Microsoft Office"], "strongest_skills": ["Excel"]},
        {"key_skills": ["Excel"], "matched_skills": ["Microsoft Office"]},
    )

    assert "Microsoft Office" not in unsupported_result["summary"]
    assert "Microsoft Office" in supported_result["summary"]


def test_english_only_appears_when_supported() -> None:
    unsupported_result = generator.generate_professional_summary(
        {"matched_skills": [], "strongest_skills": ["Excel"]},
        {"key_skills": ["Excel"], "matched_skills": []},
    )
    supported_result = generator.generate_professional_summary(
        {"matched_skills": ["Proficiency in English"], "strongest_skills": ["Excel"]},
        {"key_skills": ["Excel"], "matched_skills": ["Proficiency in English"]},
    )

    assert "English" not in unsupported_result["summary"]
    assert "Proficiency in English" in supported_result["summary"]


def test_summary_uses_direct_skill_strings_without_synthetic_labels() -> None:
    result = generator.generate_professional_summary(
        {
            "strongest_skills": ["Excel", "Meta Ads"],
            "matched_skills": ["Microsoft Office"],
        },
        {"key_skills": ["Excel", "Meta Ads"], "matched_skills": ["Microsoft Office"]},
    )

    summary = result["summary"]
    assert "Excel" in summary
    assert "Meta Ads" in summary
    assert "Microsoft Office" in summary
    assert "digital coordination tools" not in summary
    assert "administrative capabilities" not in summary
    assert "sales expertise" not in summary
    assert "business growth" not in summary


def test_empty_candidate_input_returns_safe_evidence_required_message() -> None:
    result = generator.generate_professional_summary({}, {})

    assert result["summary"] == (
        "Professional profile requires reviewed candidate evidence before "
        "a tailored summary can be generated."
    )
