import pytest
from backend.extensions import db
from backend.app import create_app
from backend.models.user import User
from backend.utils.game import SPACE
from backend.routes.solo import NUM_ROWS, NUM_COLS

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
    client.get("/api/")  # create session
    game_dict = get_solo_game(client)
    assert game_dict["state"] == "In Progress"
    assert game_dict["round_num"] == 1
    assert len(game_dict["grid"]) == NUM_ROWS
    assert all(len(row) == NUM_COLS for row in game_dict["grid"])

def test_restart(client):
    client.get("/api/")  # create session

    client.post("/api/move", data="up")
    response = client.post("/api/restart")
    assert response.status_code == 200

    new_game = response.get_json()
    assert new_game["state"] == "In Progress"
    assert new_game["round_num"] == 1

    user = db.session.get(User, get_user_id(client))
    assert user.num_abandoned_games == 1

def test_make_valid_move(client):
    client.get("/api/")  # create session
    game_before = get_solo_game(client)
    round_before = game_before["round_num"]

    response = client.post("/api/move", data="up")
    assert response.status_code == 200

    game_after = response.get_json()
    assert game_after["round_num"] == round_before + 1
    assert game_after["state"] in {"In Progress", "Won", "Lost"}
    assert len(game_after["grid"]) == NUM_ROWS

def test_make_invalid_move(client):
    client.get("/api/")  # create session

    response = client.post("/api/move", data="invalid_direction")
    assert response.status_code == 400

    data = response.get_json()
    assert "Invalid move" in data["message"] or "Bad Request" in data["error"]

def test_move_on_finished_game(client):
    client.get("/api/")  # create session
    user = db.session.get(User, get_user_id(client))
    game_dict = user.get_game_dict()

    # simulate a finished game
    game_dict["state"] = "Won"
    user.set_game_dict(game_dict)
    db.session.commit()

    response = client.post("/api/move", data="up")
    assert response.status_code == 400

    data = response.get_json()
    assert "already ended" in data["message"]

def test_multiple_moves_and_round_increment(client):
    client.get("/api/")  # create session
    rounds = 3
    for i in range(rounds):
        response = client.post("/api/move", data="up")
        assert response.status_code == 200

        game = response.get_json()
        assert game["round_num"] == i + 2  # initial round is 1

def test_database_integrity_after_moves(client):
    client.get("/api/")  # create session
    client.post("/api/move", data="up")
    client.post("/api/move", data="down")
    user = User.query.first()
    game_dict = user.get_game_dict()
    assert game_dict["round_num"] == 3
    assert game_dict["state"] in {"In Progress", "Won", "Lost"}
    assert len(game_dict["grid"]) == NUM_ROWS
