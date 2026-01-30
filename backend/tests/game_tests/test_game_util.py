import pytest
from ...utils.game import (
    construct_grid,
    evaluate,
    remove_extra_spaces,
    collapse_operators,
    collapse_list_left,
    collapse_list_right,
    out_of_bounds,
    ADDITION,
    SUBTRACTION,
    SPACE,
    # MULTIPLICATION,
)

OPERATIONS = [ADDITION, SUBTRACTION]

class TestConstructGrid:
    def test_construct_grid_classic(self):
        grid = construct_grid(6, 7, 0)
        assert grid == [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0]
        ]

    def test_construct_grid_empty_1(self):
        grid = construct_grid(0, 0, 1)
        assert grid == []
    
    def test_construct_grid_empty_2(self):
        grid = construct_grid(0, 1, 2)
        assert grid == []
    
    def test_construct_grid_empty_3(self):
        grid = construct_grid(1, 0, 3)
        assert grid == [[]]
    
    def test_construct_grid_empty_4(self):
        grid = construct_grid(2, 0, 3)
        assert grid == [[], []]
    
    def test_construct_grid_1_by_1(self):
        grid = construct_grid(1, 1, ADDITION)
        assert grid == [[ADDITION]]

 
class TestAddition:
    def test_evaluate_addition_normal(self):
        assert evaluate(3, ADDITION, 4) == 7
    
    def test_evaluate_addition_big(self):
        assert evaluate(123, ADDITION, 456) == 579
    
    def test_evaluate_addition_negative(self):
        assert evaluate(2, ADDITION, -6) == -4
    
    def test_evaluate_addition_negative_big(self):
        assert evaluate(-122, ADDITION, -436) == -558
    
    def test_evaluate_addition_zero_1(self):
        assert evaluate(0, ADDITION, 5) == 5
    
    def test_evaluate_addition_zero_2(self):
        assert evaluate(-3, ADDITION, 0) == -3
    
    def test_evaluate_addition_zero_3(self):
        assert evaluate(0, ADDITION, 0) == 0
    

class TestSubtraction:
    def test_evaluate_subtraction_normal(self):
        assert evaluate(10, SUBTRACTION, 6) == 4
    
    def test_evaluate_subtraction_negative(self):
        assert evaluate(-10, SUBTRACTION, -6) == -4

    def test_evaluate_subtraction_big(self):
        assert evaluate(926, SUBTRACTION, 487) == 439
    
    def test_evaluate_subtraction_negative_big(self):
        assert evaluate(-192, SUBTRACTION, -470) == 278

    def test_evaluate_subtraction_zero_1(self):
        assert evaluate(6, SUBTRACTION, 0) == 6
    
    def test_evaluate_subtraction_zero_2(self):
        assert evaluate(0, SUBTRACTION, 6) == -6
    
    def test_evaluate_subtraction_zero_3(self):
        assert evaluate(0, SUBTRACTION, 0) == 0
    
    def test_evaluate_subtraction_zero_4(self):
        assert evaluate(6, SUBTRACTION, -2) == 8

"""
class TestMultiplication:
    def test_evaluate_multiplication_normal(self):
        assert evaluate(3, MULTIPLICATION, 5) == 15
    
    def test_evaluate_mutiplication_negative(self):
        assert evaluate(-12, MULTIPLICATION, 5) == -60

    def test_evaluate_multiplication_big(self):
        assert evaluate(23, MULTIPLICATION, 36) == 828
    
    def test_evaluate_mutiplication_negative_big(self):
        assert evaluate(-36, MULTIPLICATION, -23) == 828
"""
         
class TestInvalidOperator:
    def test_evaluate_invalid_operator_raises_error(self):
        with pytest.raises(ValueError):
            evaluate(1, "9999", 2)
    
    def test_evaluate_division_raises_error(self):
        with pytest.raises(ValueError):
            evaluate(10, "/", 5)


class TestRemoveExtraSpaces:
    def test_remove_spaces_normal_1(self):
        lst = [1, SPACE, 2, SPACE, 3]
        assert remove_extra_spaces(lst) == [1, 2, 3]
    
    def test_remove_spaces_normal_2(self):
        lst = [SPACE, 1, "+", "-", 2, SPACE, SPACE, SPACE]
        assert remove_extra_spaces(lst) == [1, "+", "-", 2]
    
    def test_remove_spaces_no_space(self):
        lst = ["+", "-", "+"]
        assert remove_extra_spaces(lst) == ["+", "-", "+"]
    
    def test_remove_spaces_empty(self):
        lst = []
        assert remove_extra_spaces(lst) == []
    
    def test_remove_spaces_all_spaces(self):
        lst = [SPACE, SPACE, SPACE, SPACE, SPACE, SPACE]
        assert remove_extra_spaces(lst) == []

class TestCollapseOperators:
    def test_collapse_operators_normal_1(self):
        lst = [1, ADDITION, ADDITION, ADDITION, 2]
        assert collapse_operators(lst, OPERATIONS) == [1, ADDITION, 2]
    
    def test_collapse_operators_normal_2(self):
        lst = [1, ADDITION, ADDITION, ADDITION, SUBTRACTION, 3, ADDITION, 2, 2, SUBTRACTION, SUBTRACTION]
        assert collapse_operators(lst, OPERATIONS) == [1, ADDITION, SUBTRACTION, 3, ADDITION, 2, 2, SUBTRACTION]
    
    def test_collapse_operators_empty(self):
        lst = []
        assert collapse_operators(lst, OPERATIONS) == []
    
    def test_collapse_operators_no_operators(self):
        lst = [1, -2, 3, -4, 5]
        assert collapse_operators(lst, OPERATIONS) == [1, -2, 3, -4, 5]

    def test_collapse_operators_all_operators(self):
        lst = [ADDITION, ADDITION, ADDITION, SUBTRACTION, SUBTRACTION, ADDITION]
        assert collapse_operators(lst, OPERATIONS) == [ADDITION, SUBTRACTION, ADDITION]

class TestCollapseListLeft:
    def test_collapse_list_left_normal_1(self):
        lst = [1, ADDITION, ADDITION, ADDITION, 2]
        assert collapse_list_left(lst) == [3]
    
    def test_collapse_list_left_normal_2(self):
        lst = [1, SUBTRACTION, SUBTRACTION, 2, 3]
        assert collapse_list_left(lst) == [-1, 3]
    
    def test_collapse_list_left_normal_3(self):
        lst = [1, SUBTRACTION, SUBTRACTION, 2, SUBTRACTION, 3]
        assert collapse_list_left(lst) == [-1, SUBTRACTION, 3]

    def test_collapse_list_left_normal_4(self):
        lst = [1, ADDITION, ADDITION, 2, ADDITION, 3]
        assert collapse_list_left(lst) == [3, ADDITION, 3]
    
    def test_collapse_list_left_normal_5(self):
        lst = [1, ADDITION, ADDITION, SUBTRACTION, SUBTRACTION, 2, ADDITION, 5]
        assert collapse_list_left(lst) == [1, ADDITION, SUBTRACTION, 7]
    
    def test_collapse_list_left_normal_6(self):
        lst = [1, ADDITION, ADDITION, 2, ADDITION, 3]
        assert collapse_list_left(lst) == [3, ADDITION, 3]
    
    def test_collapse_list_left_empty(self):
        lst = []
        assert collapse_list_left(lst) == []
    
    def test_collapse_list_left_no_reduce_1(self):
        lst = [1, ADDITION, SUBTRACTION, SUBTRACTION, 2, 3]
        assert collapse_list_left(lst) == [1, ADDITION, SUBTRACTION, 2, 3]
    
    def test_collapse_list_left_no_reduce_2(self):
        lst = [1, 2, ADDITION, SUBTRACTION, 5, SUBTRACTION]
        assert collapse_list_left(lst) == [1, 2, ADDITION, SUBTRACTION, 5, SUBTRACTION]

class TestCollapseListRight:
    def test_collapse_list_right_normal_1(self):
        lst = [1, ADDITION, ADDITION, ADDITION, 2]
        assert collapse_list_right(lst) == [3]
    
    def test_collapse_list_right_normal_2(self):
        lst = [1, SUBTRACTION, SUBTRACTION, 2, ADDITION, 3]
        assert collapse_list_right(lst) == [1, SUBTRACTION, 5]
    
    def test_collapse_list_right_normal_3(self):
        lst = [1, SUBTRACTION, SUBTRACTION, 2, SUBTRACTION, 3]
        assert collapse_list_right(lst) == [1, SUBTRACTION, -1]

    def test_collapse_list_right_normal_4(self):
        lst = [1, ADDITION, ADDITION, 2, ADDITION, 3]
        assert collapse_list_right(lst) == [1, ADDITION, 5]
    
    def test_collapse_list_right_normal_5(self):
        lst = [1, ADDITION, SUBTRACTION, 2, ADDITION, 5]
        assert collapse_list_right(lst) == [1, ADDITION, SUBTRACTION, 7]
    
    def test_collapse_list_right_normal_6(self):
        lst = [1, ADDITION, ADDITION, 2, ADDITION, 3]
        assert collapse_list_right(lst) == [1, ADDITION, 5]
    
    def test_collapse_list_right_empty(self):
        lst = []
        assert collapse_list_right(lst) == []
    
    def test_collapse_list_right_no_reduce_1(self):
        lst = [1, ADDITION, SUBTRACTION, 2, 3]
        assert collapse_list_right(lst) == [1, ADDITION, SUBTRACTION, 2, 3]
    
    def test_collapse_list_right_no_reduce_2(self):
        lst = [1, 2, ADDITION, SUBTRACTION, 5, SUBTRACTION]
        assert collapse_list_right(lst) == [1, 2, ADDITION, SUBTRACTION, 5, SUBTRACTION]


class TestOutOfBounds:
    def test_out_of_bounds_false_within_limits(self):
        grid = [[1, 2], [3, 4]]
        assert out_of_bounds(grid) is False

    def test_out_of_bounds_ignores_spaces_and_operators(self):
        grid = [[SPACE, ADDITION], [SUBTRACTION, SPACE]]
        assert out_of_bounds(grid) is False

    def test_out_of_bounds_true_above_upper(self):
        grid = [[1001]]
        assert out_of_bounds(grid) is True

    def test_out_of_bounds_true_below_lower(self):
        grid = [[-1001]]
        assert out_of_bounds(grid) is True
