import uuid
from datetime import datetime, timedelta
from models.user import User
from app import db
from utils.game_manager import GameManager

def generate_user_id() -> str:
    return str(uuid.uuid4())

# Should be run periodically
def cleanup_expired_sessions():
    now = datetime.utcnow()
    User.query.filter(User.created_at + timedelta(days=365*2) < now).delete()
    db.session.commit()

def dict_to_game(game_dict):
    grid = game_dict["grid"]
    round_num = game_dict["round"]
    state = game_dict["state"]
    cur_game = GameManager(6, 7)
    cur_game.get_game().set_game(grid)
    cur_game.set_round(round_num)
    cur_game.set_state(state)
    cur_game.update_valid_moves()
    return cur_game