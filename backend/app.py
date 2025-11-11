from flask import Flask, jsonify, render_template, request, url_for, redirect, session, abort
import uuid
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from backend.game_manager import GameManager

app = Flask(__name__)


# Use SQLite
from flask_sqlalchemy import SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///info.db"
db = SQLAlchemy(app) 


# Use client-side Flask sessions for non-sensitive data
# A session should store data for id, current game, and statistics (wins/losses/abandoned games, and maybe time/moves taken)
# Generate a secret key with the command $ python -c 'import secrets; print(secrets.token_hex())'
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

# the current solo game is lost if the server restarts!
game = GameManager(6, 7)

def generate_user_id():
    return str(uuid.uuid4())

@app.before_request
def ensure_session():
    if "user_id" not in session:
        session["user_id"] = generate_user_id()
        session["current_solo_game"] = game.to_dict()
        session["wins"] = 0
        session["losses"] = 0
        session["abandoned"] = 0
        session.permanent = True # session is permanent unless user deletes cookie manually or server restarts


@app.route("/", methods=["GET"])
def index():
    user_id = session["user_id"]
    wins = session["wins"]
    losses = session["losses"]
    abandoned = session["abandoned"]
    return render_template("index.html", user_id=user_id, wins=wins, losses=losses, abandoned=abandoned)

def update_solo_game():
    session["current_solo_game"] = game.to_dict()

# Solo mode
@app.route("/solo", methods=["GET"])
def get_solo():
    cur_game = session["current_solo_game"]
    return render_template("solo.html", game=cur_game)

@app.route("/restart", methods=["POST"])
def restart():
    if game.get_state() == "In Progress":
        session["abandoned"] += 1

    game.restart(6, 7)
    update_solo_game()
    return game.to_dict()

@app.route("/move/<direction>", methods=["POST"])
def make_move(direction):
    if game.get_state() == "In Progress":
        game.move(direction)
        update_solo_game()
        if game.get_state() == "Won":
            session["wins"] += 1
        if game.get_state() == "Lost":
            session["losses"] += 1
        return game.to_dict()
    abort(400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
