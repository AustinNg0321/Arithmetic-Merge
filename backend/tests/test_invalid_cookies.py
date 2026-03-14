"""test_invalid_cookies.py — session/cookie edge-case coverage for the ensure_session hook."""
from datetime import datetime, timedelta
from extensions import db
from app import create_app
from models.user import User

PING = "/api/statistics"


def _user_id_from(res):
    return res.get_json()["user_id"]


def _db_user(user_id):
    """Return the User row for user_id, or None if it doesn't exist."""
    return db.session.get(User, user_id)


# ===========================================================================
# Missing cookie — first-time visitor
# ===========================================================================

def test_missing_cookie_creates_new_session(client):
    """A first-time visitor with no session cookie gets a brand-new user."""
    res = client.get(PING)
    assert res.status_code == 200
    user_id = _user_id_from(res)
    assert _db_user(user_id) is not None


# ===========================================================================
# Expired cookie — created_at beyond the 2-year threshold
# ===========================================================================

def test_expired_cookie_creates_new_session(client):
    """Backdating created_at to 3 years ago must trigger a new session."""
    res = client.get(PING)
    old_user_id = _user_id_from(res)

    user = _db_user(old_user_id)
    user.created_at = datetime.now() - timedelta(days=3 * 365)
    db.session.commit()

    res2 = client.get(PING)
    new_user_id = _user_id_from(res2)

    assert new_user_id != old_user_id
    assert _db_user(new_user_id) is not None


# ===========================================================================
# Corrupted cookie — two sub-cases
# ===========================================================================

def test_corrupted_cookie_non_uuid_user_id_creates_new_session(client):
    """A non-UUID user_id in the session → get_user returns None → new user."""
    with client.session_transaction() as sess:
        sess["user_id"] = "not-a-valid-uuid"

    res = client.get(PING)
    user_id = _user_id_from(res)

    assert user_id != "not-a-valid-uuid"
    assert _db_user(user_id) is not None


def test_corrupted_cookie_missing_user_id_key_creates_new_session(client):
    """Session dict without user_id key → ensure_session creates a fresh user."""
    with client.session_transaction() as sess:
        sess.pop("user_id", None)
        sess["extra_key"] = "some_value"

    res = client.get(PING)
    user_id = _user_id_from(res)
    assert _db_user(user_id) is not None


# ===========================================================================
# Extra session data — valid user_id must be preserved
# ===========================================================================

def test_extra_session_data_preserves_session(client):
    """A valid session with extra keys must keep the same user, not reset it."""
    res = client.get(PING)
    original_user_id = _user_id_from(res)

    with client.session_transaction() as sess:
        sess["bonus"] = "extra_data"

    res2 = client.get(PING)
    assert _user_id_from(res2) == original_user_id
    assert _db_user(original_user_id) is not None


# ===========================================================================
# Deleted cookie — client drops the session cookie between requests
# ===========================================================================

def test_deleted_cookie_creates_new_session(client):
    """Deleting the session cookie must produce a different user on the next request."""
    res = client.get(PING)
    first_user_id = _user_id_from(res)

    client.delete_cookie("session")

    res2 = client.get(PING)
    second_user_id = _user_id_from(res2)

    assert second_user_id != first_user_id
    assert _db_user(second_user_id) is not None


# ===========================================================================
# Ghost cookie — session holds a user_id whose DB row was deleted
# ===========================================================================

def test_session_exists_but_db_user_missing(client):
    """Cookie has a valid-looking user_id but the row was deleted — new user created."""
    res = client.get(PING)
    original_user_id = _user_id_from(res)

    user = _db_user(original_user_id)
    db.session.delete(user)
    db.session.commit()

    res2 = client.get(PING)
    new_user_id = _user_id_from(res2)

    assert new_user_id != original_user_id
    assert _db_user(new_user_id) is not None
