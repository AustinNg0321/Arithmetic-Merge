import pytest
from backend.extensions import db
from backend.app import create_app
from backend.models.user import User
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

def get_user_id(client):
    response = client.get("/api/")
    data = response.get_json()
    return data.get("user_id")

def get_solo_game(client):
    response = client.get("/api/solo")
    return response.get_json()

def make_valid_move(client) -> int:
    for dir in DIRECTIONS:
        res = client.post("/api/move", data=dir)
        if res.status_code == 200:
            return res.status_code
    return 400

def test_session_creation(client):
    # First request should create a session and user
    response = client.get("/api/")
    assert response.status_code == 200
    data = response.get_json()
    assert "user_id" in data
    assert data["wins"] == 0
    assert data["losses"] == 0
    assert data["abandoned"] == 0

    # User should exist in database
    user = db.session.get(User, data["user_id"])
    assert user is not None
    game_dict = user.get_game_dict()
    assert game_dict["state"] == "In Progress"
    assert len(game_dict["grid"]) == NUM_ROWS
    assert len(game_dict["grid"][0]) == NUM_COLS
    assert game_dict["round_num"] == 1

def test_get_solo(client):
    client.get("/api/")
    game_dict = get_solo_game(client)
    assert game_dict["state"] == "In Progress"
    assert game_dict["round_num"] == 1
    assert len(game_dict["grid"]) == NUM_ROWS
    assert all(len(row) == NUM_COLS for row in game_dict["grid"])

def test_restart(client):
    client.get("/api/")

    client.post("/api/move", data="up")
    response = client.post("/api/restart")
    assert response.status_code == 200

    new_game = response.get_json()
    assert new_game["state"] == "In Progress"
    assert new_game["round_num"] == 1

    user = db.session.get(User, get_user_id(client))
    assert user.num_abandoned_games == 1

def test_make_valid_move(client):
    client.get("/api/")
    game_before = get_solo_game(client)
    round_before = game_before["round_num"]

    final_status_code = 400
    for dir in DIRECTIONS:
        response = client.post("/api/move", data="up")
        if response.status_code == 200:
            final_status_code = 200
            break
    assert final_status_code == 200

    game_after = response.get_json()
    assert game_after["round_num"] == round_before + 1
    assert game_after["state"] in {"In Progress", "Won", "Lost"}
    assert len(game_after["grid"]) == NUM_ROWS

def test_make_invalid_move(client):
    client.get("/api/")
    game_before = get_solo_game(client)
    round_before = game_before["round_num"]

    move_response = client.post("/api/move", data="invalid_direction")
    assert move_response.status_code == 400
    move_response_content = move_response.get_json()
    assert "Invalid move" in move_response_content["message"] or "Bad Request" in move_response_content["error"]

    response = client.get("/api/solo")
    game_after = response.get_json()
    assert game_after["round_num"] == round_before
    assert game_after["state"] in {"In Progress", "Won", "Lost"}
    assert len(game_after["grid"]) == NUM_ROWS

def test_move_on_finished_game(client):
    client.get("/api/")

    ended = False
    while not ended:
        ended = make_valid_move(client) == 400

    response = client.post("/api/move", data="up")
    assert response.status_code == 400

def test_multiple_moves_and_round_increment(client):
    client.get("/api/")
    rounds = 10
    for i in range(rounds):
        status_code = make_valid_move(client)
        assert status_code == 200

        response = client.get("/api/solo")
        game = response.get_json()
        assert game["round_num"] == i + 2

def test_database_integrity_after_moves(client):
    client.get("/api/")
    rounds = 10
    for i in range(rounds):
        status_code = make_valid_move(client)
    user = User.query.first()
    game_dict = user.get_game_dict()
    assert game_dict["round_num"] == 11
    assert game_dict["state"] in {"In Progress", "Won", "Lost"}
    assert len(game_dict["grid"]) == NUM_ROWS
