import sqlite3
from contextlib import contextmanager
from typing import Iterator

from database.db_config import DATABASE_PATH, ensure_project_directories


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Return a SQLite connection with row access by column name."""
    ensure_project_directories()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

