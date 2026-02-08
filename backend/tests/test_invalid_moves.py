import random
import json
import pytest
from backend.models.user import User
from backend.extensions import db
from backend.app import create_app
from backend.utils.game import SPACE
from backend.routes.solo import NUM_ROWS, NUM_COLS

DIRECTIONS = ["up", "down", "left", "right"]

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
    """Ensure a session + user exist"""
    res = client.get("/api/")
    assert res.status_code == 200
    return res.get_json()["user_id"]

def make_valid_move(client) -> int:
    for dir in DIRECTIONS:
        res = client.post("/api/move", data=dir)
        if res.status_code == 200:
            return res.status_code
    return 400

def finish_game(client, max_moves=10000):
    directions = ["up", "down", "left", "right"]

    for i in range(max_moves):
        if make_valid_move(client) != 200:
            break
    
    res = client.get("/api/solo")
    state = res.get_json()["state"]
    if state in {"Won", "Lost"}:
        return state

    pytest.fail("Game did not finish within expected number of moves")


# -----------------------------
# Invalid input test cases
# -----------------------------

def test_invalid_move_direction(client):
    start_session(client)

    res = client.post("/api/move", data="jump")
    assert res.status_code == 400
    assert res.is_json


def test_empty_body(client):
    start_session(client)

    res = client.post("/api/move", data=b"")
    assert res.status_code == 400
    assert res.is_json


def test_json_body_instead_of_raw_text(client):
    start_session(client)

    res = client.post(
        "/api/move",
        data=json.dumps({"direction": "up"}),
        content_type="application/json",
    )

    # Your backend treats this as invalid input
    assert res.status_code == 400
    assert res.is_json


def test_illegal_move(client):
    start_session(client)

    # Try moves until we find an illegal one
    directions = ["up", "down", "left", "right"]
    illegal_found = False

    for _ in range(1000):
        for d in directions:
            res = client.post("/api/move", data=d)
            if res.status_code == 400:
                illegal_found = True
                break
        if illegal_found:
            break

    assert illegal_found, "Expected at least one illegal move"
    

def test_move_after_game_ended(client):
    start_session(client)

    final_state = finish_game(client)
    assert final_state in {"Won", "Lost"}

    res = client.post("/api/move", data="up")
    assert res.status_code == 400
    assert res.is_json
