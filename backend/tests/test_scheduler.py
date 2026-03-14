"""test_scheduler.py — tests for the cleanup_expired_sessions background task."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.pool import StaticPool

from app import create_app
from extensions import db
from models.user import User
from background import cleanup_expired_sessions


# ---------------------------------------------------------------------------
# Override the shared `app` fixture with StaticPool so that the nested
# app_context opened inside cleanup_expired_sessions() shares the same
# in-memory SQLite connection.  Without StaticPool, db.session.remove()
# (called when the inner context exits) returns the connection to the pool
# and the next checkout gets a *blank* database.
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    flask_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        },
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
    })
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_user(created_at=None):
    """Insert a User row, commit, and return its user_id."""
    if created_at is None:
        created_at = datetime.now(timezone.utc)

    user = User(
        user_id=str(uuid.uuid4()),
        created_at=created_at or datetime.now(),
    )
    db.session.add(user)
    db.session.commit()
    return user.user_id


# ---------------------------------------------------------------------------
# Expired user — must be deleted
# ---------------------------------------------------------------------------

def test_cleanup_expired_sessions(app):
    """A user whose created_at is 3 years in the past must be deleted."""
    user_id = _make_user(created_at=datetime.now() - timedelta(days=3 * 365))

    cleanup_expired_sessions(app, db)

    # Expire the identity map so the next get() hits the DB, not the cache.
    db.session.expire_all()
    assert db.session.get(User, user_id) is None


# ---------------------------------------------------------------------------
# Fresh user — must be preserved
# ---------------------------------------------------------------------------

def test_fresh_user_not_cleaned_up(app):
    # 1. Use a timestamp we KNOW is in the future relative to the cleanup
    user_id = _make_user(created_at=datetime.now(timezone.utc) + timedelta(minutes=5))
    
    # 2. Run cleanup
    cleanup_expired_sessions(app, db)
    
    # 3. If it fails, print the actual count in the DB
    user_count = db.session.query(User).count()
    user_exists = db.session.get(User, user_id)
    
    assert user_exists is not None, f"User was deleted! Total users in DB: {user_count}"
