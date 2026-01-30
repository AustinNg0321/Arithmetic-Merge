import pytest
from ...utils.game import (
    Game,
    SPACE,
    ADDITION,
    SUBTRACTION,
    # MULTIPLICATION,
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
    [1, ADDITION, 3, SUBTRACTION, 5, ADDITION, 7],
    [8, SUBTRACTION, 10, ADDITION, 12, SUBTRACTION, 14],
    [15, ADDITION, 17, SUBTRACTION, 19, ADDITION, 21],
    [22, SUBTRACTION, 24, ADDITION, 26, SUBTRACTION, 28],
    [29, ADDITION, 31, SUBTRACTION, 33, ADDITION, 35],
    [36, SUBTRACTION, 38, ADDITION, 40, SUBTRACTION, 42],
]

GOT_67_BUT_NO_MOVES_GRID = [
    [67, 1],
    [1, 1001],
]


def make_game(grid):
    g = Game(len(grid), len(grid[0]))
    g.set_game(grid)
    g.update_blank_spaces()
    return g

def assert_blank_spaces_consistent(game):
    cur_game = game.get_game()
    blanks = {
        (i, j)
        for i in range (len(cur_game))
        for j in range (len(cur_game[0]))
        if cur_game[i][j] == SPACE
    }
    assert set(game.get_blank_spaces()) == blanks


def test_game_initial_state():
    g = Game(6, 7)

    assert g._grid == [
        [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
        [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
        [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
        [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
        [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
        [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE],
    ]
    assert len(g.get_blank_spaces()) == 42
    assert_blank_spaces_consistent(g)

    g.generate_tiles()
    assert len(g.get_blank_spaces()) == 42 - g.get_num_generated_tiles_per_turn()
    assert_blank_spaces_consistent(g)


class TestMovementNoOperations:
    def test_slide_left_pure_no_operations(self):
        expected_new_grid = [
            [1, 2, SPACE],
            [3, SPACE, SPACE],
            [4, 5, SPACE],
        ]
        g = make_game(NO_OPERATIONS_GRID)
        assert g.get_game() == NO_OPERATIONS_GRID

        g.slide_left()
        assert g.get_game() == expected_new_grid
        assert_blank_spaces_consistent(g)

    def test_slide_right_pure_no_operations(self):
        expected_new_grid = [
            [SPACE, 1, 2],
            [SPACE, SPACE, 3],
            [SPACE, 4, 5],
        ]
        g = make_game(NO_OPERATIONS_GRID)
        assert g.get_game() == NO_OPERATIONS_GRID

        g.slide_right()
        assert g.get_game() == expected_new_grid
        assert_blank_spaces_consistent(g)
    
    def test_slide_up_pure_no_operations(self):
        expected_new_grid = [
            [1, 3, 2],
            [4, 5, SPACE],
            [SPACE, SPACE, SPACE],
        ]
        g = make_game(NO_OPERATIONS_GRID)
        assert g.get_game() == NO_OPERATIONS_GRID

        g.slide_up()
        assert g.get_game() == expected_new_grid
        assert_blank_spaces_consistent(g)
    
    def test_slide_down_pure_no_operations(self):
        expected_new_grid = [
            [SPACE, SPACE, SPACE],
            [1, 3, SPACE],
            [4, 5, 2],
        ]
        g = make_game(NO_OPERATIONS_GRID)
        assert g.get_game() == NO_OPERATIONS_GRID

        g.slide_down()
        assert g.get_game() == expected_new_grid
        assert_blank_spaces_consistent(g)
    
    def test_valid_moves_no_operations(self):
        g = make_game(NO_OPERATIONS_GRID)
        assert set(g.get_valid_moves()) == {"up", "down", "left", "right"}
    
    def test_is_in_progress_no_operations(self):
        g = make_game(NO_OPERATIONS_GRID)
        assert g.is_won() is False
        assert g.is_lost() is False


class TestMovementAlreadyWon:
    def test_slide_up_already_won(self):
        g = make_game(ALREADY_WON_GRID)
        assert g.get_game() == ALREADY_WON_GRID
        g.slide_up()
        assert g.get_game() == ALREADY_WON_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_down_already_won(self):
        g = make_game(ALREADY_WON_GRID)
        assert g.get_game() == ALREADY_WON_GRID
        g.slide_down()
        assert g.get_game() == ALREADY_WON_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_left_already_won(self):
        g = make_game(ALREADY_WON_GRID)
        assert g.get_game() == ALREADY_WON_GRID
        g.slide_left()
        assert g.get_game() == ALREADY_WON_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_right_already_won(self):
        g = make_game(ALREADY_WON_GRID)
        assert g.get_game() == ALREADY_WON_GRID
        g.slide_right()
        assert g.get_game() == ALREADY_WON_GRID
        assert_blank_spaces_consistent(g)

    def test_valid_moves_already_won(self):
        g = make_game(ALREADY_WON_GRID)
        assert g.get_valid_moves() == []

    def test_is_won_not_lost(self):
        g = make_game(ALREADY_WON_GRID)
        assert g.is_won() is True
        assert g.is_lost() is False
        

class TestMovementAlreadyLost:
    def test_slide_up_already_lost(self):
        g = make_game(ALREADY_LOST_GRID)
        assert g.get_game() == ALREADY_LOST_GRID
        g.slide_up()
        assert g.get_game() == ALREADY_LOST_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_down_already_lost(self):
        g = make_game(ALREADY_LOST_GRID)
        assert g.get_game() == ALREADY_LOST_GRID
        g.slide_down()
        assert g.get_game() == ALREADY_LOST_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_left_already_lost(self):
        g = make_game(ALREADY_LOST_GRID)
        assert g.get_game() == ALREADY_LOST_GRID
        g.slide_left()
        assert g.get_game() == ALREADY_LOST_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_right_already_lost(self):
        g = make_game(ALREADY_LOST_GRID)
        assert g.get_game() == ALREADY_LOST_GRID
        g.slide_right()
        assert g.get_game() == ALREADY_LOST_GRID
        assert_blank_spaces_consistent(g)
    
    def test_valid_moves_already_lost(self):
        g = make_game(ALREADY_LOST_GRID)
        assert g.get_valid_moves() == []

    def test_is_lost_not_won(self):
        g = make_game(ALREADY_LOST_GRID)
        assert g.is_lost() is True
        assert g.is_won() is False

# notice the collapsing mechanics for chained expressions, e.g.
# 1 + 2 + 3 + 4 -> 3 + 7 
class TestMovementFullButNotLost:
    def test_board_full(self):
        g = make_game(FULL_BUT_NOT_LOST_GRID)
        assert len(g.get_blank_spaces()) == 0
        assert_blank_spaces_consistent(g)
    
    def test_slide_up_full(self):
        g = make_game(FULL_BUT_NOT_LOST_GRID)
        assert g.get_game() == FULL_BUT_NOT_LOST_GRID
        g.slide_up()
        assert g.get_game() == FULL_BUT_NOT_LOST_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_down_full(self):
        g = make_game(FULL_BUT_NOT_LOST_GRID)
        assert g.get_game() == FULL_BUT_NOT_LOST_GRID
        g.slide_down()
        assert g.get_game() == FULL_BUT_NOT_LOST_GRID
        assert_blank_spaces_consistent(g)

    def test_slide_left_full(self):
        expected_new_grid = [
            [4, SUBTRACTION, 12, SPACE, SPACE, SPACE, SPACE],
            [-2, ADDITION, -2, SPACE, SPACE, SPACE, SPACE],
            [32, SUBTRACTION, 40, SPACE, SPACE, SPACE, SPACE],
            [-2, ADDITION, -2, SPACE, SPACE, SPACE, SPACE],
            [60, SUBTRACTION, 68, SPACE, SPACE, SPACE, SPACE],
            [-2, ADDITION, -2, SPACE, SPACE, SPACE, SPACE],
        ]
        g = make_game(FULL_BUT_NOT_LOST_GRID)
        assert g.get_game() == FULL_BUT_NOT_LOST_GRID

        g.slide_left()
        assert g.get_game() == expected_new_grid
        assert_blank_spaces_consistent(g)

    def test_slide_right_full(self):
        expected_new_grid = [
            [SPACE, SPACE, SPACE, SPACE, 4, SUBTRACTION, 12],
            [SPACE, SPACE, SPACE, SPACE, -2, ADDITION, -2],
            [SPACE, SPACE, SPACE, SPACE, 32, SUBTRACTION, 40],
            [SPACE, SPACE, SPACE, SPACE, -2, ADDITION, -2],
            [SPACE, SPACE, SPACE, SPACE, 60, SUBTRACTION, 68],
            [SPACE, SPACE, SPACE, SPACE, -2, ADDITION, -2],
        ]
        g = make_game(FULL_BUT_NOT_LOST_GRID)
        assert g.get_game() == FULL_BUT_NOT_LOST_GRID

        g.slide_right()
        assert g.get_game() == expected_new_grid
        assert_blank_spaces_consistent(g)

    def test_valid_moves_full(self):
        g = make_game(FULL_BUT_NOT_LOST_GRID)
        assert set(g.get_valid_moves()) == {"left", "right"}

    def test_is_in_progress_full(self):
        g = make_game(FULL_BUT_NOT_LOST_GRID)
        assert g.is_won() is False
        assert g.is_lost() is False


# the game should be won
class Test67ButNoMoves:
    def test_slide_up_already_won(self):
        g = make_game(GOT_67_BUT_NO_MOVES_GRID)
        assert g.get_game() == GOT_67_BUT_NO_MOVES_GRID
        g.slide_up()
        assert g.get_game() == GOT_67_BUT_NO_MOVES_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_down_already_won(self):
        g = make_game(GOT_67_BUT_NO_MOVES_GRID)
        assert g.get_game() == GOT_67_BUT_NO_MOVES_GRID
        g.slide_down()
        assert g.get_game() == GOT_67_BUT_NO_MOVES_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_left_already_won(self):
        g = make_game(GOT_67_BUT_NO_MOVES_GRID)
        assert g.get_game() == GOT_67_BUT_NO_MOVES_GRID
        g.slide_left()
        assert g.get_game() == GOT_67_BUT_NO_MOVES_GRID
        assert_blank_spaces_consistent(g)
    
    def test_slide_right_already_won(self):
        g = make_game(GOT_67_BUT_NO_MOVES_GRID)
        assert g.get_game() == GOT_67_BUT_NO_MOVES_GRID
        g.slide_right()
        assert g.get_game() == GOT_67_BUT_NO_MOVES_GRID
        assert_blank_spaces_consistent(g)

    def test_valid_moves_already_won(self):
        g = make_game(GOT_67_BUT_NO_MOVES_GRID)
        assert g.get_valid_moves() == []

    def test_is_won_not_lost(self):
        g = make_game(GOT_67_BUT_NO_MOVES_GRID)
        assert g.is_won() is True
        assert g.is_lost() is False


class TestWinLose:
    def test_is_won_true(self):
        g = make_game([[67]])
        assert g.is_won() is True

    def test_is_won_false(self):
        g = make_game([[66]])
        assert g.is_won() is False

    def test_is_lost_no_moves(self):
        g = make_game([[1, 2]])
        assert g.is_lost(valid_moves=[]) is True

    def test_is_lost_out_of_bounds(self):
        g = make_game([[2000]])
        assert g.is_lost(valid_moves=["left"]) is True

    def test_is_not_lost_when_move_exists(self):
        g = make_game([[1, SPACE]])
        assert g.is_lost() is False

