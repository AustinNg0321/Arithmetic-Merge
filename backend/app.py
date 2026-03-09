from flask import Flask
from datetime import timedelta
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, limiter
from error.error_handlers import register_error_handlers
from routes.solo import register_routes
import os

def create_app(config=None):
    load_dotenv()

    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="None",
        SESSION_COOKIE_SECURE=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=365 * 2),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config:
        app.config.update(config)

    CORS(app, supports_credentials=True, origins=[os.getenv("FRONTEND_URL")])

    db.init_app(app)
    with app.app_context():
        db.create_all()

    register_error_handlers(app, db)

    import routes.solo
    from background import start_scheduler

    if not app.config.get("TESTING"):
        limiter.init_app(app)
        start_scheduler(app, db)
    
    register_routes(app, db, limiter)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="localhost", port=5000, debug=False)
