from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict
from database import SessionLocal, Message
from datetime import datetime
import json

app = FastAPI(title='Advanced Secure Chat Platform')

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        await self.broadcast_system(f'{username} joined the chat')

    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]

    async def send_personal(self, username: str, message: str):
        if username in self.active_connections:
            await self.active_connections[username].send_text(message)

    async def broadcast(self, payload: dict):
        for user, connection in self.active_connections.items():
            await connection.send_text(json.dumps(payload))

    async def broadcast_system(self, message: str):
        payload = {
            'type': 'system',
            'message': message,
            'timestamp': str(datetime.utcnow())
        }
        await self.broadcast(payload)

manager = ConnectionManager()

html = '''
<!DOCTYPE html>
<html>
<head>
<title>Advanced Chat Platform</title>
<style>
body {
background: #020617;
color: white;
font-family: Arial;
padding: 20px;
}
#chat {
height: 500px;
overflow-y: scroll;
border: 1px solid #334155;
padding: 10px;
border-radius: 10px;
background: #0f172a;
}
input, button {
padding: 12px;
margin-top: 10px;
border-radius: 8px;
border: none;
}
input {
width: 70%;
}
button {
background: #2563eb;
color: white;
cursor: pointer;
}
.msg {
padding: 8px;
margin: 5px;
background: #1e293b;
border-radius: 8px;
}
.system {
background: #7c3aed;
}
</style>
</head>
<body>
<h1>Advanced Python Chat Platform</h1>
<input id="username" placeholder="Username">
<button onclick="connectWS()">Connect</button>
<div id="chat"></div>
<input id="messageText" placeholder="Type secure message">
<button onclick="sendMessage()">Send</button>

<script>
let ws;

function connectWS() {
    const username = document.getElementById('username').value;
    ws = new WebSocket(`ws://${location.host}/ws/${username}`);

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const chat = document.getElementById('chat');
        const div = document.createElement('div');
        div.className = data.type === 'system' ? 'msg system' : 'msg';
        div.innerHTML = `<b>${data.username || 'SYSTEM'}</b>: ${data.message}<br><small>${data.timestamp}</small>`;
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    };
}

function sendMessage() {
    const input = document.getElementById('messageText');
    ws.send(input.value);
    input.value = '';
}
</script>
</body>
</html>
'''

@app.get('/')
async def index():
    return HTMLResponse(html)

@app.websocket('/ws/{username}')
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(username, websocket)
    db = SessionLocal()

    try:
        while True:
            data = await websocket.receive_text()

            msg = Message(username=username, content=data)
            db.add(msg)
            db.commit()

            payload = {
                'type': 'chat',
                'username': username,
                'message': data,
                'timestamp': str(datetime.utcnow())
            }

            await manager.broadcast(payload)

    except WebSocketDisconnect:
        manager.disconnect(username)
        await manager.broadcast_system(f'{username} disconnected')
