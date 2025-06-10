from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
socketio = SocketIO(app)
HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []

def save_message(message):
    history = load_history()
    history.append(message)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("message")
def handle_message(data):
    save_message(data)
    emit("message", data, broadcast=True)

@socketio.on("request history")
def send_history():
    emit("history", load_history())

@app.route("/clear", methods=["POST"])
def clear_history():
    open(HISTORY_FILE, "w").write("[]")
    return "", 204

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
