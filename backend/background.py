from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from backend.models.user import User

def cleanup_expired_sessions(app, db):
    with app.app_context():
        now = datetime.now()
        expired_count = User.query.filter(User.created_at + timedelta(days=365*2) < now).delete()
        db.session.commit()
        app.logger.info(f"Removed {expired_count} expired sessions")

def start_scheduler(app, db) -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: cleanup_expired_sessions(app, db), trigger="interval", hours=24) # daily
    scheduler.start()
