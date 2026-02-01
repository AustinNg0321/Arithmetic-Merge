from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

def register_error_handlers(app, db):
    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify({
            "error": e.name,
            "message": e.description,
            "status": e.code,
        }), e.code

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        app.logger.exception(e)
        try:
            db.session.rollback()
        except Exception as e2:
            app.logger.critical(f"Database rollback failed: {e2}")

        return jsonify({
            "error": "Database Error",
            "message": "An unexpected database error occurred"
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.exception(e)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500
