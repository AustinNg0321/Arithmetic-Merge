from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from dotenv import load_dotenv
# from flask_seasurf import SeaSurf
# from flask_talisman import Talisman
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import os
# import logging only if configuring logging manually

app = Flask(__name__)

# allows frontend to call API
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # True in production (HTTPS)

# Cookie stores user id
# Generate a secret key with the command $ python -c 'import secrets; print(secrets.token_hex())'
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

# Protects from CSRF attacks
# Include the CSRF token to metadata and attach it every post request when close to production
# csrf = SeaSurf(app)

# Talisman default CSP: {'default-src': '\'self\'', 'object-src': '\'none\'',}
# The default CSP is fine for now, as long as 
# -> HTML templates do not contain inline <script> or event handlers (onclick=, onload=, etc.).
# -> All JS, CSS, and images come from /static
# -> Not loading external CDNs or fonts.
# -> Frontend only needs to call the backend API (connect-src 'self').

# csp = {
#     "default-src": "'self'",
#     "script-src": ["'self'"],
#     "style-src": ["'self'", "'unsafe-inline'"],
#     "img-src": "'self'",
#     "connect-src": "'self'",
# }
# delete force_https=False and set up certificate when close to production
# Talisman(app, content_security_policy=csp, force_https=False)

# Validate any potential form input: Never trust client-side content in JSON without checking type and allowed values
# handle resource use and add rate limits
# Set trusted hosts

# optimize automatic cleanup (later)


# This limit may get capped in some browsers
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365*2)

# Use SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///info.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app) 


# Error handlers: return consistent structured JSON error responses
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
    except:
        app.logger.critical("Database rollback failed")
    
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


# no circular import if solo.py is imported here
import backend.routes.solo

if __name__ == '__main__':
    app.run(host="localhost", port=5000)
