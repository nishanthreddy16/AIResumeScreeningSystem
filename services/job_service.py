from datetime import datetime

from database.connection import get_connection
from utils.text_extraction import extract_text_from_pdf
from utils.validators import validate_non_empty


def save_job_description(title: str, description: str) -> int:
    title = validate_non_empty(title, "Job title")
    description = validate_non_empty(description, "Job description")
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO JobDescriptions (title, description, created_at) VALUES (?, ?, ?)",
            (title, description, datetime.now().isoformat(timespec="seconds")),
        )
        return int(cursor.lastrowid)


def save_uploaded_job_description(title: str, uploaded_file) -> int:
    if uploaded_file is None:
        raise ValueError("Please upload a job description PDF.")
    temp_path = f"/tmp/{uploaded_file.name.replace(' ', '_')}"
    with open(temp_path, "wb") as output_file:
        output_file.write(uploaded_file.getbuffer())
    description = extract_text_from_pdf(temp_path)
    return save_job_description(title, description)


def get_all_job_descriptions() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM JobDescriptions ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def job_description_exists(title: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT 1 FROM JobDescriptions WHERE title = ? LIMIT 1",
            (title,),
        ).fetchone()
    return row is not None


def get_job_description(job_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM JobDescriptions WHERE job_id = ?",
            (job_id,),
        ).fetchone()
    return dict(row) if row else None
