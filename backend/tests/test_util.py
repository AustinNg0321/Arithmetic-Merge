import pytest
import uuid
from backend.utils.util import generate_user_id, dict_to_game
from backend.utils.game_manager import GameManager
from backend.utils.game import SPACE

IN_PROGRESS_GRID = [
    [1, SPACE, 2, SPACE, 3, SPACE, 4],
    [SPACE, 5, SPACE, 6, SPACE, 7, SPACE],
    [8, SPACE, 9, SPACE, 10, SPACE, 11],
    [SPACE, 12, SPACE, 13, SPACE, 14, SPACE],
    [15, SPACE, 16, SPACE, 17, SPACE, 18],
    [SPACE, 19, SPACE, 20, SPACE, 21, SPACE],
]

LOST_GRID = [
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
]

def test_generate_user_id_is_valid_uuid4():
    user_id = generate_user_id()
    parsed = uuid.UUID(user_id)

    assert isinstance(user_id, str)
    assert parsed.version == 4

def test_dict_to_game_in_progress_6x7():
    game_dict = {
        "grid": IN_PROGRESS_GRID,
        "round": 5,
        "state": "In Progress",
    }

    gm = dict_to_game(game_dict, 6, 7)

    assert isinstance(gm, GameManager)
    assert gm.get_game().get_game() == IN_PROGRESS_GRID
    assert gm.get_state() == "In Progress"
    assert gm._round_num == 5

    # Valid moves should be recomputed, not serialized
    assert set(gm._valid_moves) == {"up", "down", "left", "right"}

def test_dict_to_game_lost():
    game_dict = {
        "grid": LOST_GRID,
        "round": 12,
        "state": "Lost",
    }

    gm = dict_to_game(game_dict, 6, 7)

    assert isinstance(gm, GameManager)
    assert gm.get_game().get_game() == LOST_GRID
    assert gm.get_state() == "Lost"
    assert gm._round_num == 12

    # Lost games must have no valid moves
    assert gm._valid_moves == []

def test_dict_to_game_restores_basic_state():
    game_dict = {
        "grid": [
            [1, SPACE, 2],
            [SPACE, 3, SPACE],
        ],
        "round": 5,
        "state": "in_progress",
    }

    gm = dict_to_game(game_dict, 2, 3)

    assert isinstance(gm, GameManager)
    assert gm.get_game().get_game() == game_dict["grid"]
    assert gm.get_round() == 5
    assert gm.get_state() == "in_progress"

def test_dict_to_game_updates_valid_moves():
    game_dict = {
        "grid": [
            [1, SPACE],
            [SPACE, 2],
        ],
        "round": 1,
        "state": "in_progress",
    }

    gm = dict_to_game(game_dict, 2, 2)
    valid_moves = gm.get_valid_moves()

    assert isinstance(valid_moves, list)
    assert len(valid_moves) > 0
    assert set(valid_moves).issubset({"up", "down", "left", "right"})
