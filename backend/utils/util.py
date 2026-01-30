import uuid
from backend.utils.game_manager import GameManager

def generate_user_id() -> str:
    return str(uuid.uuid4())

def dict_to_game(game_dict: dict, num_rows: int, num_cols: int) -> GameManager:
    grid = game_dict["grid"]
    round_num = game_dict["round"]
    state = game_dict["state"]
    cur_game = GameManager(num_rows, num_cols)
    cur_game.get_game().set_game(grid)
    cur_game.set_round(round_num)
    cur_game.set_state(state)
    cur_game.update_valid_moves()
    return cur_game
