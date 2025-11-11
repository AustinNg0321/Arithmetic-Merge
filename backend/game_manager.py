import random
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from training.game import Game

class GameManager():

    def __init__(self, num_rows: int, num_cols: int):
        self._game = Game(num_rows, num_cols)
        self._game.generate_tiles()
        self._state = "In Progress"
        self._round_num = 1
        self._valid_moves = self._game.get_valid_moves()
    
    def restart(self, num_rows: int, num_cols: int) -> None:
        self._game = Game(num_rows, num_cols)
        self._game.generate_tiles()
        self._state = "In Progress"
        self._round_num = 1
        self._valid_moves = self._game.get_valid_moves()

    def get_state(self):
        return self._state

    def to_dict(self):
        return {
            "Grid": self._game._grid,
            "Rows": self._game._num_rows,
            "Columns": self._game._num_cols, 
            "Included Operations": self._game._generated_operations,
            "Operator spawn rate": self._game._prob_operations,
            "Included Digits": self._game._generated_digits,
            "Generated Tiles/Turn": self._game._num_generated_tiles,
            "Round": self._round_num,
            "State": self._state
        }

    def move(self, direction: str) -> None:
        # Make move
        if direction in self._valid_moves:
            match (direction):
                case "up":
                    self._game.slide_up()
                case "down":
                    self._game.slide_down()
                case "left":
                    self._game.slide_left()
                case _:
                    self._game.slide_right()
            
            if self._game.is_won():
                self._state = "Won"
                self._valid_moves = []
            else:
                self._round_num += 1
                self._game.generate_tiles()
                self._valid_moves = self._game.get_valid_moves()
                if self._valid_moves == []:
                    self._state = "Lost"
