from flask import session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Default rate limiting: rate limit by user_id, use IP as fallback
def rate_limit_key():
    if session and "user_id" in session:
        return session["user_id"]
    return get_remote_address()

limiter = Limiter(
    key_func=rate_limit_key,
    default_limits=["2 per second"],
    storage_uri="memory://", # change to a redis url in prod
)
