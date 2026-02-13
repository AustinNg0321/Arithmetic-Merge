from datetime import datetime, timedelta
import uuid
from flask import abort, jsonify, request, session
from sqlalchemy.exc import IntegrityError
from backend.models.user import User
from backend.utils.game import ADDITION, DeterministicRNG, Game, SPACE, SUBTRACTION, construct_grid
from backend.utils.util import generate_user_id

NUM_ROWS = 6
NUM_COLS = 7
INCLUDED_OPERATIONS = [ADDITION, SUBTRACTION]
OPERATOR_SPAWN_RATE = 0.67
INCLUDED_DIGITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
GENERATED_TILES_PER_TURN = 2
VALID_MOVES = {"up", "down", "left", "right"}


def construct_game(grid, rng=None) -> Game:
    return Game(
        grid,
        rng,
        NUM_ROWS,
        NUM_COLS,
        INCLUDED_OPERATIONS,
        OPERATOR_SPAWN_RATE,
        INCLUDED_DIGITS,
        GENERATED_TILES_PER_TURN,
    )


def get_user(db, user_id):
    user = db.session.get(User, user_id)
    if not user or user.created_at < datetime.now() - timedelta(days=2*365):
        return None
    return user


def get_stats_payload(user: User) -> dict:
    if not user:
        abort(404, description="User not found")

    return {
        "user_id": user.user_id,
        "wins": user.num_wins,
        "losses": user.num_losses,
        "abandoned": user.num_abandoned_games,
    }


def get_request_json() -> dict:
    payload = request.get_json(silent=True)
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        abort(400, description="Expected a JSON object")
    return payload


def parse_user_id_from_request() -> str | None:
    payload = get_request_json()
    user_id = payload.get("user_id")
    if user_id is None:
        user_id = request.args.get("user_id")
    if user_id is None:
        return None
    if not isinstance(user_id, str):
        abort(400, description="user_id must be a string")
    try:
        parsed = uuid.UUID(user_id, version=4)
    except (ValueError, TypeError):
        abort(400, description="user_id must be a valid UUID4 string")
    if str(parsed) != user_id:
        abort(400, description="user_id must be a canonical UUID4 string")
    return user_id


def create_new_session(app, db) -> None:
    for _ in range(2):
        try:
            session.clear()
            session["user_id"] = generate_user_id()
            session.permanent = True

            new_user = User(user_id=session["user_id"])
            db.session.add(new_user)
            db.session.commit()
            return
        except IntegrityError:
            app.logger.warning("Duplicate user id generated/provided, retrying ...")
            try:
                db.session.rollback()
            except Exception as exc:
                app.logger.critical(f"Database rollback failed: {exc}")

    app.logger.error("Failed to create user")
    abort(500, description="Failed to create session")


def apply_move(game: Game, move: str) -> None:
    match move:
        case "up":
            game.slide_up()
        case "down":
            game.slide_down()
        case "left":
            game.slide_left()
        case "right":
            game.slide_right()

def simulate_game(seed, moves: list[str]) -> tuple[bool, str | None]:
    local_rng = DeterministicRNG(str(seed))
    game = construct_game(construct_grid(NUM_ROWS, NUM_COLS, SPACE), local_rng)
    game.generate_tiles()

    for move in moves:
        if game.get_state() != "In Progress":
            return False, None

        valid_moves = set(game.get_valid_moves())
        if move not in valid_moves:
            return False, None

        apply_move(game, move)
        game.generate_tiles()

    return True, game.get_state()


def parse_seed_and_moves() -> tuple[str, list[str]]:
    payload = get_request_json()
    seed = payload.get("seed")
    moves = payload.get("moves")

    if seed is None:
        abort(400, description="Missing required field: seed")
    if not isinstance(moves, list):
        abort(400, description="Missing required field: moves (list)")
    if not all(isinstance(move, str) and move in VALID_MOVES for move in moves):
        abort(400, description="moves must be a list of: up, down, left, right")

    return str(seed), moves


def parse_verified_flag() -> bool:
    payload = get_request_json()
    verified = payload.get("verified")
    if not isinstance(verified, bool):
        abort(400, description="Missing or invalid field: verified (bool)")
    return verified


def verification_failed_response(db, user: User):
    user.num_abandoned_games += 1
    db.session.commit()
    return jsonify({
        "verified": False,
        "message": "Game verification failed",
        **get_stats_payload(user),
    }), 200


def register_routes(app, db, limiter):
    @app.before_request
    def ensure_session() -> None:
        if request.endpoint in {"static"}:
            return

        user_id = session.get("user_id")
        if user_id:
            user = get_user(db, user_id)
            if user:
                return

        create_new_session(app, db)

    @app.route("/api/statistics", methods=["GET"])
    def get_statistics():
        current_user_id = session.get("user_id")
        user = get_user(db, current_user_id)
        if not user:
            abort(404, description="User not found")
        return jsonify(get_stats_payload(user))

    @app.route("/api/verify", methods=["POST"])
    @limiter.limit("1 per 10 seconds")
    def verify_game():
        user = get_user(db, session.get("user_id"))
        if not user:
            abort(404, description="User not found")

        seed, moves = parse_seed_and_moves()
        verified, state = simulate_game(seed, moves)
        if not verified:
            return verification_failed_response(db, user)

        if state == "Won":
            user.num_wins += 1
        elif state == "Lost":
            user.num_losses += 1
        else:
            return verification_failed_response(db, user)

        db.session.commit()
        return jsonify(get_stats_payload(user))

    @app.route("/api/restart", methods=["POST"])
    @limiter.limit("1 per 10 seconds")
    def restart_game():
        user = get_user(db, session.get("user_id"))
        if not user:
            abort(404, description="User not found")

        verified = parse_verified_flag()

        if not verified:
            seed, moves = parse_seed_and_moves()
            replay_valid, state = simulate_game(seed, moves)
            if not replay_valid:
                return verification_failed_response(db, user)
            if state != "In Progress":
                abort(400, description="Game is already terminal; restart only accepts in-progress games")

        user.num_abandoned_games += 1
        db.session.commit()
        return jsonify(get_stats_payload(user))
