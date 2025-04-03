from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room
import os
import base64
import imghdr
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "secret_key"
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

active_users = {}
rooms = {}

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def login():
    username = request.form.get("username")
    if not username:
        return "Username is required.", 400
    if username in active_users:
        return "Username already taken. Please choose another.", 400
    return redirect(url_for("chat", username=username))

@app.route('/chat/<username>')
def chat(username):
    return render_template("chat.html", username=username, users=list(active_users.keys()))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on("connect")
def handle_connect():
    print("Client connected:", request.sid)

@socketio.on("join_room")
def handle_join_room(data):
    username = data["username"]
    room = data["room"]
    active_users[username] = request.sid
    rooms[username] = room
    join_room(room)
    emit("user_joined", {"username": username}, to=room)
    emit("update_user_list", {"users": list(active_users.keys())}, to=room)

@socketio.on("send_message")
def handle_send_message(data):
    username = data["username"]
    room = data["room"]
    message = data["message"]
    emit("receive_message", {"username": username, "message": message}, to=room)

# @socketio.on("send_file")
# def handle_send_file(data):
#     username = data["username"]
#     room = data["room"]
#     filename = data["filename"]
#     file_data = data["file_data"]
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
#     with open(file_path, 'wb') as f:
#         f.write(base64.b64decode(file_data))
#     emit("receive_file", {"username": username, "filename": filename, "file_url": f"/uploads/{filename}"}, to=room)


@socketio.on("send_file")
def handle_send_file(data):
    username = data["username"]
    room = data["room"]
    filename = data["filename"]
    file_data = data["file_data"]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        decoded_data = base64.b64decode(file_data)
        file_type = imghdr.what(None, decoded_data)  
        if not file_type:
            raise ValueError("Not a valid image format")

        with open(file_path, 'wb') as f:
            f.write(decoded_data)
        emit("receive_file", {"username": username, "filename": filename, "file_url": f"/uploads/{filename}"}, to=room)
    
    except Exception as e:
        print(f"Error saving file: {e}")
        emit("error", {"message": "File upload failed! Please ensure the file is a valid image."}, to=room)


@socketio.on("typing")
def handle_typing(data):
    room = data["room"]
    emit("typing", {"username": data["username"], "isTyping": data["isTyping"]}, to=room)

@socketio.on("disconnect")
def handle_disconnect():
    for username, sid in active_users.items():
        if sid == request.sid:
            room = rooms.get(username)
            if room:
                emit("user_left", {"username": username}, to=room)
                del rooms[username]
                del active_users[username]
                emit("update_user_list", {"users": list(active_users.keys())}, to=room)
            break

if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port=5000)