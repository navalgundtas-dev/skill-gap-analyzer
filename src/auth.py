import sqlite3
from contextlib import closing
from pathlib import Path

import bcrypt

DB = Path(__file__).resolve().parent.parent / "data" / "users.db"
MENTOR_CODE = "MENTOR2026"  # demo value; a real system would keep this secret


def _pw(password):
    return password.encode("utf-8")[:72]  # bcrypt only uses the first 72 bytes


def init_db(db=DB):
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users ("
                     "username TEXT PRIMARY KEY, password_hash BLOB NOT NULL, "
                     "role TEXT NOT NULL)")


def register(username, password, role, mentor_code="", db=DB):
    username = username.strip()
    if not username:
        raise ValueError("Username is required")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")
    if role not in ("student", "mentor"):
        raise ValueError("Role must be student or mentor")
    if role == "mentor" and mentor_code != MENTOR_CODE:
        raise ValueError("Wrong mentor code")
    init_db(db)
    hashed = bcrypt.hashpw(_pw(password), bcrypt.gensalt())
    try:
        with closing(sqlite3.connect(db)) as conn, conn:
            conn.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed, role))
    except sqlite3.IntegrityError:
        raise ValueError("Username already taken")


def login(username, password, db=DB):
    """Return the user's role if the login is correct, otherwise None."""
    init_db(db)
    with closing(sqlite3.connect(db)) as conn:
        row = conn.execute("SELECT password_hash, role FROM users WHERE username = ?",
                           (username.strip(),)).fetchone()
    if row and bcrypt.checkpw(_pw(password), row[0]):
        return row[1]
    return None