import sqlite3

import pytest

from src.auth import MENTOR_CODE, login, register


def test_register_then_login(tmp_path):
    db = tmp_path / "u.db"
    register("asha", "secret1", "student", db=db)
    assert login("asha", "secret1", db=db) == "student"
    assert login("asha", "wrong", db=db) is None


def test_password_is_not_stored_in_plain_text(tmp_path):
    db = tmp_path / "u.db"
    register("asha", "secret1", "student", db=db)
    stored = sqlite3.connect(db).execute("SELECT password_hash FROM users").fetchone()[0]
    assert b"secret1" not in stored


def test_mentor_needs_the_code(tmp_path):
    db = tmp_path / "u.db"
    with pytest.raises(ValueError):
        register("ravi", "secret1", "mentor", mentor_code="nope", db=db)
    register("ravi", "secret1", "mentor", mentor_code=MENTOR_CODE, db=db)
    assert login("ravi", "secret1", db=db) == "mentor"


def test_duplicate_username_rejected(tmp_path):
    db = tmp_path / "u.db"
    register("asha", "secret1", "student", db=db)
    with pytest.raises(ValueError):
        register("asha", "other12", "student", db=db)

def test_short_password_is_rejected(tmp_path):
    db = tmp_path / "u.db"
    with pytest.raises(ValueError):
        register("asha", "abc", "student", db=db)