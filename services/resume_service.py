import shutil
from datetime import datetime
from pathlib import Path

from database.connection import get_connection
from database.db_config import UPLOAD_DIR
from utils.text_extraction import extract_text_from_pdf
from utils.validators import extract_email, extract_phone, is_valid_pdf, validate_non_empty


def save_uploaded_resume(uploaded_file, candidate_name: str) -> int:
    candidate_name = validate_non_empty(candidate_name, "Candidate name")
    if uploaded_file is None:
        raise ValueError("Please upload a resume PDF.")
    if not is_valid_pdf(uploaded_file.name):
        raise ValueError("Only PDF resumes are supported.")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = uploaded_file.name.replace(" ", "_")
    file_path = UPLOAD_DIR / f"{timestamp}_{safe_name}"
    with open(file_path, "wb") as output_file:
        output_file.write(uploaded_file.getbuffer())

    extracted_text = extract_text_from_pdf(file_path)
    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Candidates (candidate_name, email, phone, created_at) VALUES (?, ?, ?, ?)",
            (candidate_name, email, phone, datetime.now().isoformat(timespec="seconds")),
        )
        candidate_id = cursor.lastrowid
        cursor.execute(
            """
            INSERT INTO Resumes (candidate_id, file_name, file_path, extracted_text, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (candidate_id, uploaded_file.name, str(file_path), extracted_text, datetime.now().isoformat(timespec="seconds")),
        )
        return int(cursor.lastrowid)


def add_sample_resume(file_path: str | Path, candidate_name: str) -> int:
    source = Path(file_path)
    target = UPLOAD_DIR / source.name
    if source.resolve() != target.resolve():
        shutil.copyfile(source, target)
    extracted_text = extract_text_from_pdf(target)
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Candidates (candidate_name, email, phone, created_at) VALUES (?, ?, ?, ?)",
            (candidate_name, extract_email(extracted_text), extract_phone(extracted_text), datetime.now().isoformat(timespec="seconds")),
        )
        candidate_id = cursor.lastrowid
        cursor.execute(
            """
            INSERT INTO Resumes (candidate_id, file_name, file_path, extracted_text, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (candidate_id, source.name, str(target), extracted_text, datetime.now().isoformat(timespec="seconds")),
        )
        return int(cursor.lastrowid)


def get_all_resumes() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT r.resume_id, r.file_name, r.file_path, r.extracted_text, r.uploaded_at,
                   c.candidate_id, c.candidate_name, c.email, c.phone
            FROM Resumes r
            JOIN Candidates c ON c.candidate_id = r.candidate_id
            ORDER BY r.uploaded_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def resume_exists_by_file_name(file_name: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT 1 FROM Resumes WHERE file_name = ? LIMIT 1",
            (file_name,),
        ).fetchone()
    return row is not None


def get_resume(resume_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT r.*, c.candidate_name, c.email, c.phone
            FROM Resumes r
            JOIN Candidates c ON c.candidate_id = r.candidate_id
            WHERE r.resume_id = ?
            """,
            (resume_id,),
        ).fetchone()
    return dict(row) if row else None


def delete_resume(resume_id: int) -> None:
    resume = get_resume(resume_id)
    if not resume:
        return
    with get_connection() as connection:
        connection.execute("DELETE FROM Analysis WHERE resume_id = ?", (resume_id,))
        connection.execute("DELETE FROM Resumes WHERE resume_id = ?", (resume_id,))
        connection.execute("DELETE FROM Candidates WHERE candidate_id = ?", (resume["candidate_id"],))
    try:
        Path(resume["file_path"]).unlink(missing_ok=True)
    except OSError:
        pass
