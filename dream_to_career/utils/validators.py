"""
utils/validators.py
Input validation and data sanitisation helpers.
All functions return (is_valid: bool, error_message: str).
"""
from __future__ import annotations
import re


def validate_name(name: str) -> tuple[bool, str]:
    name = name.strip()
    if not name:
        return False, "Name cannot be empty."
    if len(name) < 2:
        return False, "Name must be at least 2 characters."
    if len(name) > 80:
        return False, "Name must be under 80 characters."
    return True, ""


def validate_career(career: str) -> tuple[bool, str]:
    career = career.strip()
    if not career:
        return False, "Dream career cannot be empty."
    if len(career) < 3:
        return False, "Please be more specific about your target career."
    if len(career) > 150:
        return False, "Career description is too long (max 150 chars)."
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    if not email:
        return True, ""          # optional field
    pattern = r"^[\w.+-]+@[\w-]+\.[a-z]{2,}$"
    if not re.match(pattern, email, re.IGNORECASE):
        return False, "Please enter a valid email address."
    return True, ""


def validate_api_key(key: str) -> tuple[bool, str]:
    key = key.strip()
    if not key:
        return False, "Gemini API key is required."
    if len(key) < 10:
        return False, "API key seems too short — please copy the full key."
    return True, ""


def validate_interview_answer(answer: str) -> tuple[bool, str]:
    answer = answer.strip()
    if not answer:
        return False, "Please type your answer before submitting."
    if len(answer) < 10:
        return False, "Answer is too short — try to elaborate a bit more."
    if len(answer) > 5000:
        return False, "Answer is too long (max 5 000 chars)."
    return True, ""


def validate_progress_log(
    description: str,
    hours: float,
) -> tuple[bool, str]:
    if not description.strip():
        return False, "Please describe what you did."
    if hours <= 0:
        return False, "Hours must be greater than 0."
    if hours > 16:
        return False, "Hours cannot exceed 16 in a single entry."
    return True, ""


def sanitise_str(value: str, max_len: int = 500) -> str:
    """Strip whitespace and truncate."""
    return value.strip()[:max_len]


def coerce_int(value, default: int = 0, min_val: int = 0, max_val: int = 100) -> int:
    try:
        return max(min_val, min(max_val, int(value)))
    except (TypeError, ValueError):
        return default


def coerce_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
