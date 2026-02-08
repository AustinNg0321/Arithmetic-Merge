import random
import pytest
from backend.models.user import User
from backend.extensions import db
from backend.app import create_app
from backend.utils.game import ADDITION
from backend.routes.solo import safe_construct_game, NUM_ROWS, NUM_COLS

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
    assert user is not None
    return user

def assert_valid_game_dict(game_dict):
    assert isinstance(game_dict, dict)
    assert game_dict["state"] in {"In Progress", "Won", "Lost"}
    assert isinstance(game_dict["round_num"], int)
    assert game_dict["round_num"] >= 1

    grid = game_dict["grid"]
    assert isinstance(grid, list)
    assert len(grid) == NUM_ROWS
    for row in grid:
        assert isinstance(row, list)
        assert len(row) == NUM_COLS

def test_invalid_grid_dimensions(app_client):
    app, client, db = app_client
    with app.app_context():
        user_id = start_session(app_client)
        user = get_user(app_client, user_id)

        game = user.get_game_dict()
        game["grid"] = [[0, 0]]
        user.set_game_dict(game)
        db.session.commit()

        res = client.get("/api/solo")
        assert res.status_code == 200

        res_game_dict = res.get_json()
        assert_valid_game_dict(res_game_dict)
        user_copy = get_user(app_client, user_id)
        assert res_game_dict == user_copy.get_game_dict()

def test_invalid_grid_row_type(app_client):
    app, client, db = app_client
    with app.app_context():
        user_id = start_session(app_client)
        user = get_user(app_client, user_id)

        game = user.get_game_dict()
        game["grid"][0] = "not a list"
        user.set_game_dict(game)
        db.session.commit()

        res = client.get("/api/solo")
        assert res.status_code == 200

        res_game_dict = res.get_json()
        assert_valid_game_dict(res_game_dict)
        user_copy = get_user(app_client, user_id)
        assert res_game_dict == user_copy.get_game_dict()


def test_invalid_tile_value(app_client):
    app, client, db = app_client
    with app.app_context():
        user_id = start_session(app_client)
        user = get_user(app_client, user_id)

        game = user.get_game_dict()
        game["grid"][0][0] = {"illegal": "tile"}
        user.set_game_dict(game)
        db.session.commit()

        res = client.get("/api/solo")
        assert res.status_code == 200

        res_game_dict = res.get_json()
        assert_valid_game_dict(res_game_dict)
        user_copy = get_user(app_client, user_id)
        assert res_game_dict == user_copy.get_game_dict()

def test_state_mismatch(app_client):
    app, client, db = app_client
    with app.app_context():
        user_id = start_session(app_client)
        user = get_user(app_client, user_id)

        game = user.get_game_dict()
        game["state"] = "Won"  # mismatched with grid
        user.set_game_dict(game)
        db.session.commit()

        res = client.get("/api/solo")
        data = res.get_json()

        assert res.status_code == 200
        assert data["state"] != "Won"  # should be corrected
        assert_valid_game_dict(data)
        user_copy = get_user(app_client, user_id)
        assert data == user_copy.get_game_dict()

def test_missing_game_dict(app_client):
    app, client, db = app_client
    with app.app_context():
        user_id = start_session(app_client)
        user = get_user(app_client, user_id)

        # Simulate missing game
        user.cur_solo_game = "" # invalid JSON string
        db.session.commit()

        res = client.get("/api/solo")
        assert res.status_code == 200

        res_game_dict = res.get_json()
        assert_valid_game_dict(res_game_dict)
        user_copy = get_user(app_client, user_id)
        assert res_game_dict == user_copy.get_game_dict()

def test_missing_game_fields(app_client):
    app, client, db = app_client
    with app.app_context():
        user_id = start_session(app_client)
        user = get_user(app_client, user_id)

        user.set_game_dict({"grid": []})  # missing state + round_num
        db.session.commit()

        res = client.get("/api/solo")
        assert res.status_code == 200

        res_game_dict = res.get_json()
        assert_valid_game_dict(res_game_dict)
        user_copy = get_user(app_client, user_id)
        assert res_game_dict == user_copy.get_game_dict()

# Fix test
def test_missing_state_key(app_client):
    app, client, db = app_client
    with app.app_context():
        user_id = start_session(app_client)
        user = get_user(app_client, user_id)
        # Missing state
        game_dict = {
            "grid": [[ADDITION]*NUM_COLS]*NUM_ROWS,
            "round_num": 1,
        }
        user.set_game_dict(game_dict)
        db.session.add(user)
        db.session.commit()

        new_game = client.get("/api/solo").get_json()
        assert new_game["state"] == "In Progress"

# Fix test
def test_invalid_round_num(app_client):
    app, client, db = app_client
    with app.app_context():
        user_id = start_session(app_client)
        user = get_user(app_client, user_id)

        game_dict = {
            "grid": [[ADDITION]*NUM_COLS]*NUM_ROWS,
            "state": "In Progress",
            "round_num": -123
        }
        user.set_game_dict(game_dict)
        db.session.add(user)
        db.session.commit()

        game = safe_construct_game(user.get_game_dict(), app)
        assert game.get_game() is not None
