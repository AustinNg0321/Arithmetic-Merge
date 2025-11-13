from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Use client-side Flask sessions for non-sensitive data
# A session should store data for id, current game, and statistics (wins/losses/abandoned games, and maybe time/moves taken)
# Generate a secret key with the command $ python -c 'import secrets; print(secrets.token_hex())'
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

# This limit may get capped in some browsers
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365*2)

# Use SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///info.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app) 

import backend.routes.solo

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
