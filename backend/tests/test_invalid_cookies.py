import pytest
from flask import session
from datetime import datetime, timedelta
from backend.models.user import User
from backend.app import db
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def start_session(client):
    res = client.get("/api/")
    assert res.status_code == 200
    return res.get_json()["user_id"]

def get_user(db, user_id):
    return db.session.get(User, user_id)


# No cookies sent at all → backend should create a new session + user.
def test_missing_cookie_creates_new_session(client):
    user_id = start_session(client)
    assert get_user(db, user_id) is not None

def test_expired_cookie_creates_new_session(client):
    old_user_id = start_session(client)
    user = get_user(db, old_user_id)

    user.created_at = datetime.now() - timedelta(days=3*365)
    db.session.commit()
    
    new_user_id = start_session(client)
    assert get_user(db, new_user_id) is not None
    assert old_user_id != new_user_id

# Cookie exists but contains invalid session data: user_id still exists but is corrupted
def test_corrupted_cookie_creates_new_session_1(client):
    with client.session_transaction() as session:
        session["user_id"] = "corrupted user id"
        session["asdf"] = "asdf"

    user_id = start_session(client)
    assert get_user(db, user_id) is not None

# Cookie exists but contains invalid session data: user_id no longer exists
def test_corrupted_cookie_creates_new_session_2(client):
    with client.session_transaction() as session:
        session.pop("user_id", None)
        session["asdf"] = "asdf"

    user_id = start_session(client)
    assert get_user(db, user_id) is not None

# user_id exists but cookie contains extra data: preserves the session
def test_extra_session_data_preserves_session(client):
    old_user_id = start_session(client)

    with client.session_transaction() as session:
        session["asdf"] = "asdf"

    new_user_id = start_session(client)
    assert get_user(db, new_user_id) is not None
    assert old_user_id == new_user_id

# Simulate deleted session by clearing cookies.
def test_deleted_cookie_creates_new_session(client):
    first_user_id = start_session(client)
    client.delete_cookie("session")
    second_user_id = start_session(client)

    assert first_user_id != second_user_id
    assert get_user(db, second_user_id) is not None

# Session contains user_id, but DB row was deleted.
# Backend should recover by creating a new user + session.
def test_session_exists_but_db_user_missing(client):
    original_user_id = start_session(client)

    user = get_user(db, original_user_id)
    db.session.delete(user)
    db.session.commit()

    new_user_id = start_session(client)
    assert new_user_id != original_user_id
    assert db.session.get(User, new_user_id) is not None
