"""
Experience Bullet Generator

Purpose:
Generate deterministic, evidence-safe experience bullets from Evidence objects.
"""


NO_EXPERIENCE_EVIDENCE_ERROR = "No experience evidence found. Cannot generate bullets."
MAX_BULLETS = 5


def _empty_ai_output() -> dict:
    """Return the empty AI Generation Contract schema for Sprint 18."""
    return {
        "summary": "",
        "experience_bullets": [],
        "skills": {
            "technical": [],
            "soft": [],
            "domain": [],
        },
    }


def _failed_output(provider: str) -> dict:
    """Return failed wrapper output when no usable experience evidence exists."""
    return {
        "status": "failed",
        "errors": [NO_EXPERIENCE_EVIDENCE_ERROR],
        "provider": provider,
        "mode": "deterministic",
        "ai_output": _empty_ai_output(),
    }


def _success_output(provider: str, bullets: list[dict]) -> dict:
    """Return successful wrapper output with generated bullets."""
    ai_output = _empty_ai_output()
    ai_output["experience_bullets"] = bullets

    return {
        "status": "success",
        "errors": [],
        "provider": provider,
        "mode": "deterministic",
        "ai_output": ai_output,
    }


def _is_usable_experience_evidence(evidence) -> bool:
    """Return whether an Evidence item can be used for bullet generation."""
    evidence_id = getattr(evidence, "id", "")
    evidence_text = getattr(evidence, "text", "")
    evidence_category = getattr(evidence, "category", "")

    return (
        bool(str(evidence_id).strip())
        and bool(str(evidence_text).strip())
        and str(evidence_category).strip().casefold() == "experience"
    )


def _select_experience_evidence(evidence_items: list) -> list:
    """Return the first five usable experience Evidence items in list order."""
    selected_evidence = []
    for evidence in evidence_items:
        if _is_usable_experience_evidence(evidence):
            selected_evidence.append(evidence)
        if len(selected_evidence) == MAX_BULLETS:
            break
    return selected_evidence


def _build_bullet(evidence) -> dict:
    """Build one deterministic bullet from Evidence text and id."""
    return {
        "text": str(evidence.text).strip(),
        "source_evidence_id": str(evidence.id).strip(),
    }


def _build_deterministic_bullets(evidence_items: list) -> list[dict]:
    """Build deterministic bullets from selected experience Evidence items."""
    return [_build_bullet(evidence) for evidence in evidence_items]


def _generate_with_gemini(evidence_items: list) -> list[dict]:
    """Sprint 18 Gemini path using deterministic bullet generation only."""
    selected_evidence = _select_experience_evidence(evidence_items)
    return _build_deterministic_bullets(selected_evidence)


def generate_experience_bullets(
    evidence_items: list,
    provider: str = "gemini",
) -> dict:
    """Generate deterministic experience bullets from Evidence objects."""
    if provider != "gemini":
        raise ValueError(f"Unsupported provider: {provider}")

    if not evidence_items:
        return _failed_output(provider)

    bullets = _generate_with_gemini(evidence_items)
    if not bullets:
        return _failed_output(provider)

    return _success_output(provider, bullets)
