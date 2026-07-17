from database.connection import get_connection
from database.init_db import hash_password


def authenticate_user(username: str, password: str) -> bool:
    with get_connection() as connection:
        user = connection.execute(
            "SELECT password_hash FROM Users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
    return bool(user and user["password_hash"] == hash_password(password))

