import pytest
import uuid
from backend.utils.util import generate_user_id, is_valid_state
from backend.utils.game import Game
from backend.routes.solo import construct_game, construct_grid, NUM_ROWS, NUM_COLS
from backend.utils.game import SPACE

IN_PROGRESS_GRID = [
    [1, SPACE, 2, SPACE, 3, SPACE, 4],
    [SPACE, 5, SPACE, 6, SPACE, 7, SPACE],
    [8, SPACE, 9, SPACE, 10, SPACE, 11],
    [SPACE, 12, SPACE, 13, SPACE, 14, SPACE],
    [15, SPACE, 16, SPACE, 17, SPACE, 18],
    [SPACE, 19, SPACE, 20, SPACE, 21, SPACE],
]

WON_GRID = [
    [67, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
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

class TestState:
    def test_valid_states(self):
        assert is_valid_state("In Progress") is True
        assert is_valid_state("Won") is True
        assert is_valid_state("Lost") is True

        assert is_valid_state("in progress") is False
        assert is_valid_state("win") is False
        assert is_valid_state("  lost  ") is False
    
    def test_start_game_valid_state(self):
        cur_game = construct_game(construct_grid(NUM_ROWS, NUM_COLS, SPACE))
        assert is_valid_state(cur_game.get_state()) is True

    def test_in_progress_game_valid_state(self):
        cur_game = construct_game(IN_PROGRESS_GRID)
        assert is_valid_state(cur_game.get_state()) is True
    
    def test_won_game_valid_state(self):
        cur_game = construct_game(WON_GRID)
        assert is_valid_state(cur_game.get_state()) is True

    def test_lost_game_valid_state(self):
        cur_game = construct_game(LOST_GRID)
        assert is_valid_state(cur_game.get_state()) is True
