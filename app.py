from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json, os

app = Flask(__name__)
socketio = SocketIO(app)

USERS_FILE = 'users.json'
CHAT_FILE = 'chat.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def get_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            data = json.load(f)
        return jsonify(list(data.keys()))
    return jsonify([])

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            users = json.load(f)
    if username in users:
        return jsonify(success=False, message="既に存在します")
    users[username] = password
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)
    return jsonify(success=True, message="登録成功")

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    if not os.path.exists(USERS_FILE):
        return jsonify(success=False, message="ユーザーが存在しません")
    with open(USERS_FILE) as f:
        users = json.load(f)
    if users.get(username) == password:
        return jsonify(success=True)
    return jsonify(success=False, message="パスワードが違います")

@app.route('/auto_login', methods=['POST'])
def auto_login():
    data = request.json
    username = data.get('username')
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            users = json.load(f)
        if username in users:
            return jsonify(success=True)
    return jsonify(success=False)

@app.route('/history')
def history():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE) as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/delete_chat', methods=['POST'])
def delete_chat():
    with open(CHAT_FILE, 'w') as f:
        json.dump([], f)
    return '', 204

@socketio.on('message')
def handle_message(msg):
    chat = []
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE) as f:
            chat = json.load(f)
    chat.append(msg)
    with open(CHAT_FILE, 'w') as f:
        json.dump(chat, f)
    emit('message', msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
