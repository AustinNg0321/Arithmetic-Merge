from flask import session, request, abort, jsonify
from random import random
from backend.app import db, app
from backend.models.user import User
from backend.utils.util import generate_user_id
from backend.utils.game import Game, construct_grid, ADDITION, SUBTRACTION, SPACE
from datetime import datetime, timedelta

NUM_ROWS = 6
NUM_COLS = 7
INCLUDED_OPERATIONS = [ADDITION, SUBTRACTION]
OPERATOR_SPAWN_RATE = 0.67
INCLUDED_DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
GENERATED_TILES_PER_TURN = 2

# changed user_id: if user_id not found in the database, create a new session 
# changed current_solo_game: 

# If the cookie is modified/deleted/etc. -> crashes
# i.e. session integrity and corruption handling
# e.g. restart may fail if dict_to_game() fails
 
# return consistent error responses (maybe add global error handler)
# switch to taking JSON

# Should be run periodically
def cleanup_expired_sessions() -> None:
    now = datetime.now()
    User.query.filter(User.created_at + timedelta(days=365*2) < now).delete()
    db.session.commit()

def construct_game(grid):
    return Game(grid, NUM_ROWS, NUM_COLS, INCLUDED_OPERATIONS, OPERATOR_SPAWN_RATE, INCLUDED_DIGITS, GENERATED_TILES_PER_TURN)


# session is permanent unless it expires, the user deletes cookie manually, or the server restarts 
@app.before_request
def ensure_session():
    if "user_id" not in session or not User.query.get(session["user_id"]):
        session.clear()
        session["user_id"] = generate_user_id()
        session.permanent = True 

        new_game = construct_game(construct_grid(NUM_ROWS, NUM_COLS, SPACE))
        new_game.generate_tiles()
        new_game_dict = {
            "grid": new_game.get_game(),
            "state": "In Progress",
            "round_num": 1,
        }

        new_user = User(user_id=session["user_id"])
        new_user.set_game_dict(new_game_dict)
        db.session.add(new_user)
        db.session.commit()

    if random() < 0.001:
        cleanup_expired_sessions()


@app.route("/api/", methods=["GET"])
def index():
    user = User.query.get_or_404(session["user_id"])
    user_profile = {
        "user_id": user.user_id,
        "wins": user.num_wins,
        "losses": user.num_losses,
        "abandoned": user.num_abandoned_games
    }
    return jsonify(user_profile)

# Solo mode
@app.route("/api/solo", methods=["GET"])
def get_solo():
    user = User.query.get_or_404(session["user_id"])
    return user.get_game_dict()

@app.route("/api/restart", methods=["POST"])
def restart():
    user = User.query.get_or_404(session["user_id"])
    cur_game_dict = user.get_game_dict()
    cur_game = construct_game(cur_game_dict["grid"])
    if cur_game.get_state() == "In Progress":
        user.num_abandoned_games += 1

    new_game = construct_game(construct_grid(NUM_ROWS, NUM_COLS, SPACE))
    new_game.generate_tiles()
    new_game_dict = {
        "grid": new_game.get_game(),
        "state": "In Progress",
        "round_num": 1,
    }

    user.set_game_dict(new_game_dict)
    db.session.commit()
    return jsonify(new_game_dict)

@app.route("/api/move", methods=["POST"])
def make_move():
    # Expects "up", "down", "left", or "right" in the request body
    # Parsing and validating input
    direction = request.data.decode("utf-8").strip().lower()
    if not direction or direction not in ["up", "down", "left", "right"]:
        return jsonify("Invalid move direction"), 400

    user = User.query.get_or_404(session["user_id"])
    game_dict = user.get_game_dict()
    game = construct_game(game_dict["grid"])
    if game.get_state() != "In Progress":
        return jsonify("Game has already ended"), 400

    legal_moves = game.get_valid_moves()
    if direction in legal_moves:
        if direction == "up":
            game.slide_up()
        elif direction == "down":
            game.slide_down()
        elif direction == "left":
            game.slide_left()
        else:
            game.slide_right()
        game.generate_tiles()
    else:
        return jsonify("Illegal move"), 400
    
    new_state = game.get_state()
    if new_state == "Won":
        user.num_wins += 1
    if new_state == "Lost":
        user.num_losses += 1

    new_game_dict = {
        "grid": game.get_game(),
        "state": new_state,
        "round_num": game_dict["round_num"] + 1,
    }
    user.set_game_dict(new_game_dict)
    db.session.commit()
    return jsonify(new_game_dict)
