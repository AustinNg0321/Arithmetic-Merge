import json
from backend.app import db
from datetime import datetime

# session expires in 365*2 days (about 2 years)
class User(db.Model):
    user_id = db.Column(db.String(36), primary_key=True)  # UUID
    cur_solo_game = db.Column(db.Text, default="", nullable=False) # JSON string with grid, state, round num
    num_wins = db.Column(db.Integer, default=0, nullable=False)
    num_losses = db.Column(db.Integer, default=0, nullable=False)
    num_abandoned_games = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    
    def get_game_dict(self):
        try:
            return json.loads(self.cur_solo_game)
        except json.JSONDecodeError as e:
            return {}

    def set_game_dict(self, game_dict: dict):
        self.cur_solo_game = json.dumps(game_dict)
