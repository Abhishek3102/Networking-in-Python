from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from slixmpp import ClientXMPP
import asyncio

app = Flask(__name__)
app.secret_key = "secret_key"
socketio = SocketIO(app)

class ChatClient(ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.receive_message)
        self.presences = {}

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

    def receive_message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            socketio.emit(
                "receive_message", {"sender": msg["from"], "message": msg["body"]}, to=msg["to"]
            )

clients = {}
online_users = {}

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def login():
    jid = request.form["jid"]
    password = request.form["password"]
    if jid not in clients:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = ChatClient(jid, password)
        client.connect()
        client.loop.run_in_executor(None, client.process)
        clients[jid] = client
    online_users[jid] = True
    return redirect(url_for("chat", jid=jid))

@app.route('/chat/<jid>')
def chat(jid):
    users = list(clients.keys())
    users.remove(jid)
    return render_template("chat.html", jid=jid, users=users)

@socketio.on("send_message")
def handle_send_message(data):
    sender = data["sender"]
    recipient = data["recipient"]
    message = data["message"]
    if sender in clients:
        clients[sender].send_chat_message(recipient, message)
    emit("message_status", {"recipient": recipient, "status": "sent"}, to=sender)
    emit("message_status", {"recipient": recipient, "status": "delivered"}, to=recipient)
    emit("receive_message", {"sender": sender, "message": message}, to=recipient)

@socketio.on("mark_as_read")
def mark_as_read(data):
    recipient = data["recipient"]
    emit("message_status", {"recipient": recipient, "status": "read"}, to=recipient)

@socketio.on("join_room")
def handle_join_room(data):
    join_room(data["jid"])

if __name__ == "__main__":
    socketio.run(app, debug=True)
