from ...utils.game_manager import GameManager
from ...utils.game import (
    Game,
    SPACE,
    ADDITION,
    SUBTRACTION,
    MULTIPLICATION
)

NO_OPERATIONS_GRID = [
    [1, SPACE, 2],
    [SPACE, 3, SPACE],
    [4, 5, SPACE],
]

ALREADY_WON_GRID = [
    [1, 2, 3, 4, 5, 6, 7],
    [8, 9, 10, 11, 12, 13, 14],
    [15, 16, 17, 18, 19, 20, 21],
    [22, 23, 24, 25, 26, 27, 28],
    [29, 30, 31, 32, 33, 34, 35],
    [36, 37, 38, 39, 40, 41, 67],
]

ALREADY_LOST_GRID = [
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
    [1001, 1001, 1001, 1001, 1001, 1001, 1001],
]

FULL_BUT_NOT_LOST_GRID = [
    [1, ADDITION, 3, SUBTRACTION, 5, MULTIPLICATION, 7],
    [8, SUBTRACTION, 10, ADDITION, 12, SUBTRACTION, 14],
    [15, MULTIPLICATION, 17, SUBTRACTION, 19, ADDITION, 21],
    [22, SUBTRACTION, 24, MULTIPLICATION, 26, MULTIPLICATION, 28],
    [29, ADDITION, 31, SUBTRACTION, 33, SUBTRACTION, 35],
    [36, SUBTRACTION, 38, ADDITION, 40, ADDITION, 42],
]

GOT_67_BUT_NO_MOVES_GRID = [
    [67, 1],
    [1, 1001],
]

def make_game_manager(grid) -> GameManager:
    gm = GameManager(len(grid), len(grid[0]))
    gm.get_game().set_game(grid)
    gm.get_game().update_blank_spaces()
    gm.update_valid_moves()
    return gm

def update_state(gm):
    if gm.get_game().is_won():
            gm.set_state("Won")
    elif gm.get_game().is_lost():
        gm.set_state("Lost")
    else:
        gm.set_state("In Progress")


class TestGameManagerInitialState:
    def test_initial_state(self):
        gm = GameManager(6, 7)

        assert gm.get_state() == "In Progress"
        assert gm._round_num == 1
        assert isinstance(gm.get_game(), Game)
        assert gm._valid_moves == gm.get_game().get_valid_moves()

class TestGameManagerRestart:
    def test_restart_resets_state(self):
        gm = GameManager(3, 3)
        gm.set_state("Lost")
        gm.set_round(10)

        gm.restart(3, 3)
        assert gm.get_state() == "In Progress"
        assert gm._round_num == 1
        assert gm._valid_moves == gm.get_game().get_valid_moves()


class TestGameManagerMoveDispatch:
    def test_invalid_direction_does_nothing(self):
        gm = GameManager(3, 3)
        grid_before = gm.get_game()._grid
        round_before = gm._round_num

        gm.move("invalid")

        assert gm.get_game()._grid == grid_before
        assert gm._round_num == round_before

    def test_move_not_in_progress(self):
        gm = GameManager(3, 3)
        gm.set_state("Lost")
        round_before = gm._round_num

        gm.move("left")
        assert gm._round_num == round_before

class TestGameManagerAlreadyWon:
    def test_state_won_blocks_moves(self):
        gm = make_game_manager(ALREADY_WON_GRID)
        update_state(gm)
        gm.move("left")

        assert gm.get_state() == "Won"
        assert gm._valid_moves == []

class TestGameManagerAlreadyLost:
    def test_state_lost_blocks_moves(self):
        gm = make_game_manager(ALREADY_LOST_GRID)
        update_state(gm)
        gm.move("left")

        assert gm.get_state() == "Lost"
        assert gm._valid_moves == []

class TestGameManagerRoundProgression:
    def test_round_increments_after_move(self):
        gm = make_game_manager(NO_OPERATIONS_GRID)

        assert gm._round_num == 1
        gm.move("left")

        assert gm._round_num == 2

class TestGameManagerLossDetection:
    def test_loss_after_move(self):
        gm = make_game_manager([[1001]])

        gm._valid_moves = ["left"]
        gm.move("left")

        assert gm.get_state() == "Lost"

class TestGameManagerToDict:
    def test_to_dict_contents(self):
        gm = GameManager(2, 3)
        data = gm.to_dict()

        assert data["rows"] == 2
        assert data["columns"] == 3
        assert data["round"] == 1
        assert data["state"] == "In Progress"
        assert "grid" in data

