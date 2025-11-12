from flask import Flask, jsonify, render_template, request, url_for, redirect, session, abort
from datetime import timedelta, datetime
import uuid
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from backend.game_manager import GameManager

app = Flask(__name__)

# This limit may get capped in some browsers
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365*1000)

# Use SQLite
from flask_sqlalchemy import SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///info.db"
db = SQLAlchemy(app) 


# Use client-side Flask sessions for non-sensitive data
# A session should store data for id, current game, and statistics (wins/losses/abandoned games, and maybe time/moves taken)
# Generate a secret key with the command $ python -c 'import secrets; print(secrets.token_hex())'
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

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

def generate_user_id() -> str:
    return str(uuid.uuid4())

# session is permanent unless it expires, the user deletes cookie manually, or the server restarts 
@app.before_request
def ensure_session():
    if "user_id" not in session:
        session["user_id"] = generate_user_id()
        session["current_solo_game"] = GameManager(6, 7).to_dict()
        session["wins"] = 0
        session["losses"] = 0
        session["abandoned"] = 0
        session.permanent = True 


@app.route("/", methods=["GET"])
def index():
    user_id = session["user_id"]
    wins = session["wins"]
    losses = session["losses"]
    abandoned = session["abandoned"]
    return render_template("index.html", user_id=user_id, wins=wins, losses=losses, abandoned=abandoned)

# Solo mode
@app.route("/solo", methods=["GET"])
def get_solo():
    cur_game = session["current_solo_game"]
    return render_template("solo.html", game=cur_game)

@app.route("/restart", methods=["POST"])
def restart():
    game = dict_to_game(session["current_solo_game"])
    if game.get_state() == "In Progress":
        session["abandoned"] += 1

    game.restart(6, 7)
    session["current_solo_game"] = game.to_dict()
    return session["current_solo_game"]

@app.route("/move/<direction>", methods=["POST"])
def make_move(direction):
    game = dict_to_game(session["current_solo_game"])
    if game.get_state() == "In Progress":
        game.move(direction)
        session["current_solo_game"] = game.to_dict()
        if game.get_state() == "Won":
            session["wins"] += 1
        if game.get_state() == "Lost":
            session["losses"] += 1
        return session["current_solo_game"]
    abort(400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
