import time
import pytest
from backend.models.user import User
from backend.extensions import db, limiter
from backend.app import create_app
from backend.utils.game import SPACE
from backend.routes.solo import safe_construct_game, NUM_ROWS, NUM_COLS

@pytest.fixture
def client():
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })

    # testing with limiter initialized
    limiter.init_app(app)

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def get_user(db, user_id):
    user = db.session.get(User, user_id)
    assert user is not None
    return user


# limit: 2 per second
def test_index_rate_limiting(client):
    for i in range (2):
        response = client.get("/api/")
    third_response = client.get("/api/")
    assert third_response.status_code == 429

    time.sleep(1)
    fourth_response = client.get("/api/")
    assert fourth_response.status_code == 200

# limit: 2 per second
def test_index_rate_limiting(client):
    for i in range (2):
        response = client.get("/api/solo")
    third_response = client.get("/api/solo")
    assert third_response.status_code == 429

    time.sleep(1)
    fourth_response = client.get("/api/solo")
    assert fourth_response.status_code == 200

# limit: 1 per 10 seconds
def test_restart_rate_limiting(client):
    response = client.post("/api/restart")
    second_response = client.post("/api/restart")
    assert second_response.status_code == 429

    time.sleep(10)
    fourth_response = client.post("/api/restart")
    assert fourth_response.status_code == 200

# limit: 10 per second
def test_move_rate_limiting(client):
    for i in range (10):
        response = client.post("/api/move", data="up")
    limited_response = client.post("/api/move", data="down")
    assert limited_response.status_code == 429

    time.sleep(1)
    reset_response = client.post("/api/move", data="up")
    assert reset_response.status_code != 429
