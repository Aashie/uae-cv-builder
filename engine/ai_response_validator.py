"""
AI Response Validator

Purpose:
Validate AI-generated responses against the AI Generation Contract.
"""


SUPPORTED_TOP_LEVEL_FIELDS = {"summary", "experience_bullets", "skills"}
REQUIRED_TOP_LEVEL_FIELDS = ("summary", "experience_bullets", "skills")
REQUIRED_SKILL_FIELDS = ("technical", "soft", "domain")


def _is_empty_string(value: object) -> bool:
    """Return True when a value is a string with no non-whitespace content."""
    return isinstance(value, str) and not value.strip()


def validate_ai_response(response: dict) -> dict:
    """Validate an AI response structure and collect all contract errors."""
    errors: list[str] = []

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in response:
            errors.append(f"Missing required field: {field}")

    for field in response:
        if field not in SUPPORTED_TOP_LEVEL_FIELDS:
            errors.append(f"Unsupported field: {field}")

    if "summary" in response:
        summary = response["summary"]
        if not isinstance(summary, str):
            errors.append("Invalid type for summary: expected str")
        elif _is_empty_string(summary):
            errors.append("Empty required field: summary")

    if "experience_bullets" in response:
        experience_bullets = response["experience_bullets"]
        if not isinstance(experience_bullets, list):
            errors.append("Invalid type for experience_bullets: expected list")
        else:
            for index, bullet in enumerate(experience_bullets):
                if not isinstance(bullet, dict):
                    errors.append(
                        f"Invalid type for bullet at index {index}: expected dict"
                    )
                    continue

                if "text" not in bullet:
                    errors.append(f"Missing required field: text in bullet at index {index}")
                else:
                    text = bullet["text"]
                    if not isinstance(text, str):
                        errors.append(
                            f"Invalid type for text in bullet at index {index}: expected str"
                        )
                    elif _is_empty_string(text):
                        errors.append(f"Empty required field: text in bullet at index {index}")

                if "source_evidence_id" not in bullet:
                    errors.append(
                        f"Missing required field: source_evidence_id in bullet at index {index}"
                    )
                else:
                    source_evidence_id = bullet["source_evidence_id"]
                    if not isinstance(source_evidence_id, str):
                        errors.append(
                            "Invalid type for source_evidence_id in bullet "
                            f"at index {index}: expected str"
                        )
                    elif _is_empty_string(source_evidence_id):
                        errors.append(
                            "Empty required field: source_evidence_id in bullet "
                            f"at index {index}"
                        )

    if "skills" in response:
        skills = response["skills"]
        if not isinstance(skills, dict):
            errors.append("Invalid type for skills: expected dict")
        else:
            for field in REQUIRED_SKILL_FIELDS:
                if field not in skills:
                    errors.append(f"Missing required field: skills.{field}")
                elif not isinstance(skills[field], list):
                    errors.append(f"Invalid type for skills.{field}: expected list")

    return {
        "is_valid": not errors,
        "errors": errors,
    }
