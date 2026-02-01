from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from backend.routes.solo import safe_construct_game
from backend.models.user import User
from backend.app import db, app

def cleanup_expired_sessions():
    now = datetime.now()
    expired_count = User.query.filter(User.created_at + timedelta(days=365*2) < now).delete()
    db.session.commit()
    app.logger.info(f"Removed {expired_count} expired sessions")

def fix_corrupted_data():
    updated = 0

    for user in User.query.yield_per(100):
        try:
            game_dict = user.get_game_dict()
            game = safe_construct_game(game_dict)
            round_num = game_dict["round_num"]
            if not isinstance(round_num, int) or round_num < 1:
                round_num = 1

            if (game_dict["grid"] != game.get_game() or
                game_dict["state"] != game.get_state() or
                game_dict["round_num"] != round_num):

                new_game_dict = {
                    "grid": game.get_game(),
                    "state": game.get_state(),
                    "round_num": round_num,
                }
                user.set_game_dict(new_game_dict)
                updated += 1

        except Exception as e:
            app.logger.warning(f"Failed to update user {user.user_id}: {e}")

    if updated > 0:
        try:
            db.session.commit()
            app.logger.info(f"Fixed {updated} corrupted game(s)")
        except Exception as e:
            app.logger.error(f"Database commit failed during cleanup: {e}")
            try:
                db.session.rollback()
            except Exception as e2:
                app.logger.critical(f"Database rollback failed: {e2}")

def start_scheduler() -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup_expired_sessions, trigger="interval", hours=24) # daily
    scheduler.add_job(func=fix_corrupted_data, trigger="interval", hours=24) # daily
    scheduler.start()
