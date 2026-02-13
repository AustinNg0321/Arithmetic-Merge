from backend.extensions import db
from datetime import datetime

# session expires in 365*2 days (about 2 years)
class User(db.Model):
    user_id = db.Column(db.String(36), primary_key=True)  # UUID
    num_wins = db.Column(db.Integer, default=0, nullable=False)
    num_losses = db.Column(db.Integer, default=0, nullable=False)
    num_abandoned_games = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
