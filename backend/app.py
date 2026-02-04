from flask import Flask
from datetime import timedelta
from dotenv import load_dotenv
from flask_cors import CORS
from backend.extensions import db, limiter
from backend.error.error_handlers import register_error_handlers
from backend.routes.solo import register_routes
import os
# import logging only if configuring logging manually
# from flask_seasurf import SeaSurf
# from flask_talisman import Talisman

def create_app(config=None):
    load_dotenv()

    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        PERMANENT_SESSION_LIFETIME=timedelta(days=365 * 2),
        SQLALCHEMY_DATABASE_URI="sqlite:///info.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config:
        app.config.update(config)

    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

    db.init_app(app)
    with app.app_context():
        db.create_all()

    register_error_handlers(app, db)

    import backend.routes.solo
    from backend.background import start_scheduler

    if not app.config.get("TESTING"):
        limiter.init_app(app)
        start_scheduler(app, db)
    
    register_routes(app, db, limiter)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="localhost", port=5000)
