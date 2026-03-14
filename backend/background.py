import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
from models.user import User

def cleanup_expired_sessions(app, db):
    with app.app_context():
        # 1. Calculate the cutoff in Python
        # Use a fixed 'now' and subtract the delta
        cutoff = datetime.now() - timedelta(days=365*2)
        
        # 2. Use a simple comparison in the filter
        expired_count = User.query.filter(User.created_at < cutoff).delete()
        
        try:
            db.session.commit()
            if expired_count > 0:
                app.logger.info(f"Removed {expired_count} expired sessions")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Cleanup failed: {e}")

def start_scheduler(app, db) -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: cleanup_expired_sessions(app, db), trigger="interval", hours=24) # daily
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))
