from flask import session, render_template, request, abort, jsonify
from random import random
from backend.app import db, app
from backend.models.user import User
from backend.utils.util import generate_user_id, cleanup_expired_sessions, dict_to_game
from backend.utils.game_manager import GameManager

# check for missing session keys in the future 

# session is permanent unless it expires, the user deletes cookie manually, or the server restarts 
@app.before_request
def ensure_session():
    if "user_id" not in session:
        session["user_id"] = generate_user_id()
        session["current_solo_game"] = GameManager(6, 7).to_dict()
        session.permanent = True 
        db.session.add(User(user_id=session["user_id"]))
        db.session.commit()
    
    if random() < 0.001:
        cleanup_expired_sessions()

@app.route("/", methods=["GET"])
def index():
    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)
    user_profile = {
        "user_id": user_id,
        "wins": user.num_wins,
        "losses": user.num_losses,
        "abandoned": user.num_abandoned_games
    }
    return jsonify(user_profile)

# Solo mode
@app.route("/solo", methods=["GET"])
def get_solo():
    return jsonify(session["current_solo_game"])

@app.route("/restart", methods=["POST"])
def restart():
    game = dict_to_game(session["current_solo_game"])
    if game.get_state() == "In Progress":
        user_id = session["user_id"]
        user = User.query.get_or_404(user_id)
        user.num_abandoned_games += 1
        db.session.commit()

    game.restart(6, 7)
    session["current_solo_game"] = game.to_dict()
    return jsonify(session["current_solo_game"])

@app.route("/move", methods=["POST"])
def make_move():
    # Expects "up", "down", "left", or "right" in the request body
    direction = request.data.decode("utf-8").strip().lower()

    # or use functions from GameManager or Game
    if not direction or direction not in ["up", "down", "left", "right"]:
        abort(400, description="Invalid move direction")

    game = dict_to_game(session["current_solo_game"])
    if game.get_state() != "In Progress":
        abort(400, description="Game has already ended")

    game.move(direction)
    session["current_solo_game"] = game.to_dict()

    user_id = session["user_id"]
    user = User.query.get_or_404(user_id)
    if game.get_state() == "Won":
        user.num_wins += 1
    if game.get_state() == "Lost":
        user.num_losses += 1
    db.session.commit()
    
    return jsonify(session["current_solo_game"])
