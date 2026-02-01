from flask import session, request, abort, jsonify
from sqlalchemy.exc import IntegrityError
from random import random
from backend.app import db, app, limiter
from backend.models.user import User
from backend.utils.util import generate_user_id, is_valid_state
from backend.utils.game import Game, construct_grid, ADDITION, SUBTRACTION, SPACE
from datetime import datetime, timedelta

NUM_ROWS = 6
NUM_COLS = 7
INCLUDED_OPERATIONS = [ADDITION, SUBTRACTION]
OPERATOR_SPAWN_RATE = 0.67
INCLUDED_DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
GENERATED_TILES_PER_TURN = 2

def is_valid_element(el: any) -> bool:
    return isinstance(el, int) or el in INCLUDED_OPERATIONS or el == SPACE

def construct_game(grid) -> Game:
    return Game(grid, NUM_ROWS, NUM_COLS, INCLUDED_OPERATIONS, OPERATOR_SPAWN_RATE, INCLUDED_DIGITS, GENERATED_TILES_PER_TURN)

def validate_grid(grid) -> None:
    if not isinstance(grid, list) or len(grid) != NUM_ROWS:
        raise ValueError("Invalid grid dimensions")
    for row in grid:
        if not isinstance(row, list) or len(row) != NUM_COLS:
            app.logger.warning(f"Expected list but got {type(row)}")
            raise ValueError("Invalid grid row")
        for el in row:
            if not is_valid_element(el):
                app.logger.warning(f"Invalid element: {el} of type {type(el)}")
                raise ValueError("Invalid grid row")

def validate_game_dict(game_dict: dict) -> Game:
    grid = game_dict["grid"]
    state = game_dict["state"]

    validate_grid(grid)
    new_game = construct_game(grid)

    if not is_valid_state(state) or state != new_game.get_state():
        raise ValueError("Invalid state")

    if "round_num" not in game_dict:
        raise ValueError("Key number not in game_dict")

    return new_game

def safe_construct_game(game_dict: dict) -> Game:
    if not isinstance(game_dict, dict):
        app.logger.warning(f"Expected dict but got {type(game_dict)}")
        return construct_game(construct_grid(NUM_ROWS, NUM_COLS, SPACE))

    try:
        return validate_game_dict(game_dict)
    except (KeyError, ValueError, TypeError) as e:
        app.logger.warning(f"Corrupted game data detected: {e}")
        return construct_game(construct_grid(NUM_ROWS, NUM_COLS, SPACE))

def create_new_game() -> dict:
    new_game = construct_game(construct_grid(NUM_ROWS, NUM_COLS, SPACE))
    new_game.generate_tiles()
    new_game_dict = {
        "grid": new_game.get_game(),
        "state": "In Progress",
        "round_num": 1,
    }
    return new_game_dict


# retry once if unlikely UUID collision or other IntegrityErrors
def create_new_session() -> None:
    for attempt in range(2):
        try:
            session.clear()
            session["user_id"] = generate_user_id()
            session.permanent = True 

            new_user = User(user_id=session["user_id"])
            new_user.set_game_dict(create_new_game())
            db.session.add(new_user)
            db.session.commit()
            return
        except IntegrityError:
            app.logger.warning("Duplicate user id generated, retrying ...")
            try:
                db.session.rollback()
            except Exception as e:
                app.logger.critical(f"Database rollback failed: {e}")
    
    app.logger.error("Failed to create user")
    abort(500, description="Failed to create session")

# session is permanent unless it expires, the user deletes cookie manually, or the server restarts 
@app.before_request
def ensure_session() -> None:
    if request.endpoint in {"static"}:
        return

    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user:
            return

    create_new_session()

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
# game dict validity should be validated in the front end
@app.route("/api/solo", methods=["GET"])
def get_solo():
    user = User.query.get_or_404(session["user_id"])
    return user.get_game_dict()


@app.route("/api/restart", methods=["POST"])
@limiter.limit("1 per 10 seconds")
def restart():
    user = User.query.get_or_404(session["user_id"])
    cur_game_dict = user.get_game_dict()

    cur_game = safe_construct_game(cur_game_dict)
    if cur_game.get_state() == "In Progress":
        user.num_abandoned_games += 1

    new_game_dict = create_new_game()
    user.set_game_dict(new_game_dict)
    db.session.commit()
    return jsonify(new_game_dict)


def parse_direction() -> str:
    direction = request.data.decode("utf-8").strip().lower()
    if direction not in {"up", "down", "left", "right"}:
        abort(400, description="Invalid move direction")
    return direction

def apply_move(game: Game, direction: str) -> None:
    if direction in game.get_valid_moves():
        match direction:
            case "up":
                game.slide_up()
            case "down":
                game.slide_down()
            case "left":
                game.slide_left()
            case "right":
                game.slide_right()
        game.generate_tiles()
    else:
        abort(400, description="Illegal move")
    
def update_user_stats(user: User, game: Game) -> str:
    state = game.get_state()
    if state == "Won":
        user.num_wins += 1
    elif state == "Lost":
        user.num_losses += 1
    return state

# if round_num invalid, new round_num is not enforced currently !!!
@app.route("/api/move", methods=["POST"])
@limiter.limit("10 per second")
def handle_move():
    direction = parse_direction()
    user = User.query.get_or_404(session["user_id"])
    game_dict = user.get_game_dict()
    game = safe_construct_game(game_dict)

    if game.get_state() != "In Progress":
        abort(400, description="Game has already ended")
    
    # reset round_num if invalid
    if not isinstance(game_dict["round_num"], int) or game_dict["round_num"] < 1:
        game_dict["round_num"] = 1

    apply_move(game, direction)

    # update new user state in db
    new_state = update_user_stats(user, game)
    new_game_dict = {
        "grid": game.get_game(),
        "state": new_state,
        "round_num": game_dict["round_num"] + 1,
    }
    user.set_game_dict(new_game_dict)
    db.session.commit()
    return jsonify(new_game_dict)
