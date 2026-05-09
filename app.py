from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import json

app = FastAPI(title='Advanced Python Chat App')

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Advanced Chat</title>
    <style>
        body { font-family: Arial; background:#0f172a; color:white; }
        #chat { height:400px; overflow:auto; border:1px solid #333; padding:10px; }
        input { width:80%; padding:10px; }
        button { padding:10px; }
    </style>
</head>
<body>
    <h1>Advanced Python Chat App</h1>
    <div id='chat'></div>
    <input id='messageText' type='text' placeholder='Message'>
    <button onclick='sendMessage()'>Send</button>

<script>
const ws = new WebSocket(`ws://${location.host}/ws`);
ws.onmessage = function(event) {
    const chat = document.getElementById('chat');
    chat.innerHTML += `<p>${event.data}</p>`;
};
function sendMessage() {
    const input = document.getElementById('messageText');
    ws.send(input.value);
    input.value = '';
}
</script>
</body>
</html>
"""

@app.get('/')
async def get():
    return HTMLResponse(html)

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
