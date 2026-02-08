import pytest
from datetime import datetime, timedelta
from backend.background import cleanup_expired_sessions
from backend.models.user import User
from backend.app import db, create_app

@pytest.fixture
def app_client():
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    
    with app.app_context():
        db.create_all()
        client = app.test_client()
        yield app, client, db
        db.drop_all()

def start_session(app_client):
    app, client, db = app_client
    res = client.get("/api/")
    assert res.status_code == 200
    return res.get_json()["user_id"]

def get_user(app_client, user_id):
    app, client, db = app_client
    user = db.session.get(User, user_id)
    return user

def test_cleanup_expired_sessions(app_client):
    app, client, db = app_client
    with app.app_context():
        old_user_id = start_session(app_client)
        old_user = get_user(app_client, old_user_id)
        old_user.created_at = datetime.now() - timedelta(days=365*3)
        db.session.commit()

        cleanup_expired_sessions(app, db)
        assert get_user(app_client, old_user_id) is None  # user should be deleted
