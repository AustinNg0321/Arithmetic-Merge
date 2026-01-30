from backend.utils.game import Game

class GameManager():
    def __init__(self, num_rows: int, num_cols: int) -> None:
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

    def get_game(self) -> Game:
        return self._game

    def get_state(self) -> str:
        return self._state
    
    def get_round(self) -> int:
        return self._round_num

    def set_round(self, round_num: int) -> None:
        self._round_num = round_num

    def set_state(self, state: str) -> None:
        self._state = state
    
    def get_valid_moves(self) -> list[str]:
        return self._valid_moves

    def update_valid_moves(self) -> None:
        self._valid_moves = self._game.get_valid_moves()

    def to_dict(self) -> dict:
        return {
            "grid": self._game.get_game(),
            "rows": self._game.get_num_rows(),
            "columns": self._game.get_num_cols(), 
            "included_operations": self._game.get_generated_operations(),
            "operator_spawn_rate": self._game.get_prob_operations(),
            "included_digits": self._game.get_generated_digits(),
            "generated_tiles_per_turn": self._game.get_num_generated_tiles_per_turn(),
            "round": self._round_num,
            "state": self._state
        }

    def move(self, direction: str) -> None:
        if self._state == "In Progress" and direction in self._valid_moves:
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
                if self._game.is_lost():
                    self._state = "Lost"
