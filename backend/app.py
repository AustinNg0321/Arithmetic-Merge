from flask import Flask, jsonify, render_template, request, url_for, redirect
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.game_manager import GameManager, GameState
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Start with SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///info.db"
db = SQLAlchemy(app) 

game = GameState()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Solo mode
@app.route("/solo", methods=["GET"])
def get_solo():
    game.reset()
    return render_template("solo.html")

@app.route("/start", methods=["POST"])
def start():
    if not game.has_started():
        game.start()

    game.set_game(GameManager(6, 7))
    return game.get_game().to_dict()

@app.route("/move/<direction>", methods=["POST"])
def make_move(direction):
    if not game.has_started():
        return jsonify({"error": "No active game"}), 400

    game.get_game().move(direction)
    return game.get_game().to_dict()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
