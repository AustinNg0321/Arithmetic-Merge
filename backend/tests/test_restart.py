import pytest
import time
from backend.models.user import User
from backend.utils.game import SPACE
from backend.routes.solo import NUM_ROWS, NUM_COLS
from backend.extensions import db
from backend.app import create_app

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
    res = client.get("/api/")
    assert res.status_code == 200
    return res.get_json()["user_id"]

def get_user(db, user_id):
    return db.session.get(User, user_id)

def assert_fresh_game(game):
    assert isinstance(game, dict)
    assert game["state"] == "In Progress"
    assert game["round_num"] == 1
    assert len(game["grid"]) == NUM_ROWS
    for row in game["grid"]:
        assert len(row) == NUM_COLS

def make_valid_move(client) -> int:
    for dir in DIRECTIONS:
        res = client.post("/api/move", data=dir)
        if res.status_code == 200:
            return res.status_code
    return 400


# ---------- tests ----------

def test_win_or_loss_increments_once_on_game_end(client):
    user_id = start_session(client)

    for i in range (10000):
        make_valid_move(client)
        user = db.session.get(User, user_id)
        state = user.get_game_dict()["state"]

        if state in {"Won", "Lost"}:
            break

    # RE-FETCH USER (important)
    user = db.session.get(User, user_id)
    game = user.get_game_dict()

    assert game["state"] in {"Won", "Lost"}

    if game["state"] == "Won":
        assert user.num_wins == 1
        assert user.num_losses == 0
    else:
        assert user.num_losses == 1
        assert user.num_wins == 0


def test_restart_resets_game(client):
    user_id = start_session(client)

    # make a move to change game state
    make_valid_move(client)

    res = client.post("/api/restart")
    assert res.status_code == 200

    new_game = res.get_json()
    assert_fresh_game(new_game)

    # persisted
    user = get_user(db, user_id)
    assert user.get_game_dict() == new_game

def test_restart_increments_abandoned_if_in_progress(client):
    user_id = start_session(client)

    make_valid_move(client)
    client.post("/api/restart")

    user = get_user(db, user_id)
    assert user.num_abandoned_games == 1

def test_restart_does_not_increment_if_game_ended(client):
    user_id = start_session(client)
    user = get_user(db, user_id)

    ended = False
    while not ended:
        ended = make_valid_move(client) == 400

    time.sleep(0.1)
    client.post("/api/restart")
    time.sleep(0.1)
    user_id_copy = start_session(client)
    user_copy = get_user(db, user_id_copy)
    assert user.num_abandoned_games == 0

def test_multiple_restarts_only_increment_once_per_game(client):
    client.post("/api/move", data="left")
    for i in range (2):
        if i == 1:
            time.sleep(10)
        client.post("/api/restart")
        user_id = start_session(client)
        user = get_user(db, user_id)
        assert user.num_abandoned_games == i + 1

def test_restart_returns_valid_game_dict(client):
    start_session(client)

    res = client.post("/api/restart")
    data = res.get_json()

    assert data["state"] == "In Progress"
    assert data["round_num"] == 1
    assert isinstance(data["grid"], list)


def test_restart_without_prior_moves(client):
    user_id = start_session(client)

    res = client.post("/api/restart")
    assert res.status_code == 200

    user = get_user(db, user_id)
    assert user.num_abandoned_games == 1

def test_restart_repairs_corrupted_game_data(client):
    user_id = start_session(client)
    user = db.session.get(User, user_id)
    assert user is not None

    # Inject corrupted game data
    user.set_game_dict({
        "grid": "invalid_grid",
        "state": "Won",        
        "round_num": -999
    })
    db.session.commit()

    # Restart should repair corrupted game
    res = client.post("/api/restart")
    assert res.status_code == 200

    user = db.session.get(User, user_id)
    game_dict = user.get_game_dict()
    assert_fresh_game(game_dict)
    assert user.num_abandoned_games == 1

