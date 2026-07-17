from pathlib import Path

import pdfplumber
from PyPDF2 import PdfReader


def extract_text_with_pdfplumber(file_path: str | Path) -> str:
    text_parts = []
    with pdfplumber.open(str(file_path)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()


def extract_text_with_pypdf2(file_path: str | Path) -> str:
    reader = PdfReader(str(file_path))
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_parts).strip()


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extract PDF text using pdfplumber first and PyPDF2 as fallback."""
    try:
        text = extract_text_with_pdfplumber(file_path)
        if text:
            return text
    except Exception:
        pass

    try:
        return extract_text_with_pypdf2(file_path)
    except Exception as exc:
        raise ValueError(f"Could not extract text from PDF: {exc}") from exc

