"""
Test Professional Summary Generator

Purpose:
Unit tests for provider-dispatched professional summary generation.
"""

import pytest

from engine import professional_summary_generator as generator


def resume_draft(summary: str = "Experienced operations professional.") -> dict:
    """Return a resume draft fixture."""
    return {"professional_summary": summary}


def prompt_package() -> dict:
    """Return a prompt package fixture."""
    return {"job_title": "Operations Coordinator"}


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

    assert result == valid_ai_response("Fallback summary.")


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

    assert result["summary"] == "Fallback summary."


def test_empty_response_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generator, "_generate_with_gemini", lambda prompt, draft: {})
    monkeypatch.setattr(generator, "_retry_delay", lambda: None)

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Fallback summary."),
    )

    assert result == valid_ai_response("Fallback summary.")


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

    assert result["summary"] == "Resume draft summary."


def test_fallback_uses_empty_summary_when_resume_draft_summary_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(generator, "_generate_with_gemini", lambda prompt, draft: None)
    monkeypatch.setattr(generator, "_retry_delay", lambda: None)

    result = generator.generate_professional_summary(prompt_package(), {})

    assert result["summary"] == ""


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

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Fallback summary."),
    )

    assert result["summary"] == "Fallback summary."
    assert calls == ["call"]


def test_authentication_failure_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def fake_gemini(prompt: dict, draft: dict) -> dict:
        calls.append("call")
        raise generator.ProviderAuthenticationError

    monkeypatch.setattr(generator, "_generate_with_gemini", fake_gemini)

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Fallback summary."),
    )

    assert result["summary"] == "Fallback summary."
    assert calls == ["call"]


def test_rate_limit_error_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def fake_gemini(prompt: dict, draft: dict) -> dict:
        calls.append("call")
        raise generator.ProviderRateLimitError

    monkeypatch.setattr(generator, "_generate_with_gemini", fake_gemini)

    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Fallback summary."),
    )

    assert result["summary"] == "Fallback summary."
    assert calls == ["call"]


def test_no_real_gemini_api_call_required() -> None:
    result = generator.generate_professional_summary(
        prompt_package(),
        resume_draft("Deterministic placeholder summary."),
    )

    assert result == valid_ai_response("Deterministic placeholder summary.")
