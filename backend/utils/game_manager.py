from backend.utils.game import Game

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

    def get_game(self):
        return self._game

    def get_state(self):
        return self._state
    
    def set_round(self, round_num: int) -> None:
        self._round_num = round_num

    def set_state(self, state: str) -> None:
        self._state = state
    
    def update_valid_moves(self) -> None:
        self._valid_moves = self._game.get_valid_moves()

    def to_dict(self):
        return {
            "grid": self._game._grid,
            "rows": self._game._num_rows,
            "columns": self._game._num_cols, 
            "included_operations": self._game._generated_operations,
            "operator_spawn_rate": self._game._prob_operations,
            "included_digits": self._game._generated_digits,
            "generated_tiles_per_turn": self._game._num_generated_tiles,
            "round": self._round_num,
            "state": self._state
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
