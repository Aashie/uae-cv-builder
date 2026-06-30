"""
Hallucination Checker

Purpose:
Validate AI-generated experience bullets against linked evidence records.
"""

import string


STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "with",
    "of",
    "in",
    "to",
    "for",
    "is",
    "was",
    "on",
    "at",
    "by",
}


def _extract_meaningful_keywords(text: str) -> set[str]:
    """Normalize text into meaningful keywords for exact matching."""
    translation_table = str.maketrans("", "", string.punctuation)
    normalized_text = text.lower().translate(translation_table)

    return {
        word
        for word in normalized_text.split()
        if word not in STOPWORDS and len(word) >= 4
    }


def check_hallucinations(ai_output: dict, evidence_items: list) -> dict:
    """Validate AI-generated experience bullets against linked evidence records."""
    evidence_lookup = {
        getattr(evidence, "id"): getattr(evidence, "text", "")
        for evidence in evidence_items
    }

    passed_bullets: list[dict] = []
    failed_bullets: list[dict] = []

    for bullet in ai_output.get("experience_bullets", []):
        bullet_text = bullet["text"]
        source_evidence_id = bullet["source_evidence_id"]
        evidence_text = evidence_lookup.get(source_evidence_id)

        if evidence_text is None:
            failed_bullets.append(
                {
                    "bullet": bullet_text,
                    "reason": "Linked evidence not found.",
                }
            )
            continue

        bullet_keywords = _extract_meaningful_keywords(bullet_text)
        evidence_keywords = _extract_meaningful_keywords(evidence_text)

        if bullet_keywords & evidence_keywords:
            passed_bullets.append(bullet)
        else:
            failed_bullets.append(
                {
                    "bullet": bullet_text,
                    "reason": "No keyword overlap with linked evidence.",
                }
            )

    return {
        "passed_bullets": passed_bullets,
        "failed_bullets": failed_bullets,
        "hallucination_count": len(failed_bullets),
    }
