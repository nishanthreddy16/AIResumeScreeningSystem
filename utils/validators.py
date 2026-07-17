import re
from pathlib import Path


def is_valid_pdf(file_name: str) -> bool:
    return Path(file_name).suffix.lower() == ".pdf"


def validate_non_empty(value: str, field_name: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be empty.")
    return cleaned


def extract_email(text: str) -> str | None:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = re.search(r"(?:\+91[-\s]?)?[6-9]\d{9}", text)
    return match.group(0) if match else None

