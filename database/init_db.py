import hashlib
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.connection import get_connection


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 for this offline student project."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def initialize_database() -> None:
    """Create all tables and seed the default admin user."""
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin',
                created_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Candidates (
                candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Resumes (
                resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                extracted_text TEXT,
                uploaded_at TEXT NOT NULL,
                FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS JobDescriptions (
                job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Analysis (
                analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                match_score REAL NOT NULL,
                matched_skills TEXT,
                missing_skills TEXT,
                recommended_skills TEXT,
                keyword_matches TEXT,
                summary TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id),
                FOREIGN KEY (job_id) REFERENCES JobDescriptions(job_id)
            )
            """
        )

        cursor.execute(
            """
            INSERT OR IGNORE INTO Users (username, password_hash, role, created_at)
            VALUES (?, ?, ?, ?)
            """,
            ("admin", hash_password("admin123"), "admin", datetime.now().isoformat(timespec="seconds")),
        )


def reset_database() -> None:
    """Developer helper used by tests."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.executescript(
            """
            DROP TABLE IF EXISTS Analysis;
            DROP TABLE IF EXISTS Resumes;
            DROP TABLE IF EXISTS JobDescriptions;
            DROP TABLE IF EXISTS Candidates;
            DROP TABLE IF EXISTS Users;
            """
        )
    initialize_database()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
