from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database.db"
UPLOAD_DIR = BASE_DIR / "uploads"
REPORT_DIR = BASE_DIR / "reports"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"


def ensure_project_directories() -> None:
    """Create runtime folders used by the application."""
    for folder in (UPLOAD_DIR, REPORT_DIR, SAMPLE_DATA_DIR):
        folder.mkdir(parents=True, exist_ok=True)

