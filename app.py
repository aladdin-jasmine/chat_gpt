from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import json
import uuid
import os
import time

from backend.platform.aios_core import platform
from backend.security.ai_guardrails import AIGuardrails
from backend.execution.sandbox import SecureSandbox
from backend.security.threat_intel import ThreatIntelEngine
from backend.soc.siem_pipeline import SIEMPipeline
from backend.agents.goal_engine import GoalEngine
from backend.memory.self_improving_memory import SelfImprovingMemory

app = FastAPI(
    title='AI Operating System Platform',
    version='4.0.0',
    description='Enterprise AI orchestration, cybersecurity intelligence, autonomous agents, and realtime collaboration platform'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


class UserMessage(BaseModel):
    username: str
    message: str
    room: str = 'global'


class ObjectiveRequest(BaseModel):
    objective: str
    provider: str = 'openai'


class SandboxRequest(BaseModel):
    code: str


class ThreatRequest(BaseModel):
    indicator: str


class AgentRequest(BaseModel):
    name: str
    objective: str


class KnowledgeRequest(BaseModel):
    query: str


class WorkspaceState:
    def __init__(self):
        self.rooms: Dict[str, List[str]] = {}
        self.active_users: Dict[str, WebSocket] = {}
        self.audit_logs: List[dict] = []
        self.agent_sessions: Dict[str, dict] = {}
        self.shared_context: Dict[str, dict] = {}

    async def create_room(self, room_name: str):
        if room_name not in self.rooms:
            self.rooms[room_name] = []

    async def join_room(self, username: str, room_name: str):
        await self.create_room(room_name)

        if username not in self.rooms[room_name]:
            self.rooms[room_name].append(username)

    async def leave_room(self, username: str, room_name: str):
        if room_name in self.rooms:
            if username in self.rooms[room_name]:
                self.rooms[room_name].remove(username)

    async def add_audit_log(self, action: str, actor: str):
        self.audit_logs.append({
            'id': str(uuid.uuid4()),
            'action': action,
            'actor': actor,
            'timestamp': str(datetime.utcnow())
        })


workspace_state = WorkspaceState()
manager_guardrails = AIGuardrails()
execution_sandbox = SecureSandbox()
intel_engine = ThreatIntelEngine()
siem_pipeline = SIEMPipeline()
goal_engine = GoalEngine()
semantic_memory = SelfImprovingMemory()


class RealtimeConnectionManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.connections[username] = websocket

    async def disconnect(self, username: str):
        if username in self.connections:
            del self.connections[username]

    async def broadcast_global(self, payload: dict):
        disconnected = []

        for username, connection in self.connections.items():
            try:
                await connection.send_text(json.dumps(payload))
            except Exception:
                disconnected.append(username)

        for username in disconnected:
            del self.connections[username]

    async def send_personal(self, username: str, payload: dict):
        if username in self.connections:
            await self.connections[username].send_text(json.dumps(payload))

    async def room_broadcast(self, room: str, payload: dict):
        if room not in self.rooms:
            return

        for username in self.rooms[room]:
            if username in self.connections:
                await self.connections[username].send_text(json.dumps(payload))

    async def register_room_member(self, room: str, username: str):
        if room not in self.rooms:
            self.rooms[room] = []

        if username not in self.rooms[room]:
            self.rooms[room].append(username)


manager = RealtimeConnectionManager()


DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>AI Operating System</title>
<style>
body {
    background: #020617;
    color: white;
    font-family: Arial;
    margin: 0;
}
.header {
    padding: 20px;
    background: #0f172a;
    border-bottom: 1px solid #1e293b;
}
.workspace {
    display: grid;
    grid-template-columns: 300px 1fr 350px;
    height: calc(100vh - 80px);
}
.sidebar {
    background: #0f172a;
    border-right: 1px solid #1e293b;
    padding: 20px;
    overflow-y: auto;
}
.chat-panel {
    padding: 20px;
    overflow-y: auto;
}
.ai-panel {
    background: #0f172a;
    border-left: 1px solid #1e293b;
    padding: 20px;
}
.card {
    background: #1e293b;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}
textarea, input {
    width: 100%;
    padding: 12px;
    background: #111827;
    color: white;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 10px;
}
button {
    padding: 12px;
    border: none;
    border-radius: 8px;
    background: #2563eb;
    color: white;
    cursor: pointer;
    margin-top: 10px;
}
#messages {
    height: 70vh;
    overflow-y: auto;
}
.message {
    background: #1e293b;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 10px;
}
</style>
</head>
<body>
<div class='header'>
<h1>AI Operating System Platform</h1>
</div>
<div class='workspace'>
<div class='sidebar'>
<div class='card'>
<h3>Workspace</h3>
<p>Realtime AI orchestration environment</p>
</div>
<div class='card'>
<h3>Security Operations</h3>
<p>Threat intelligence enabled</p>
</div>
<div class='card'>
<h3>Autonomous Agents</h3>
<p>Recursive planning online</p>
</div>
</div>
<div class='chat-panel'>
<div id='messages'></div>
<input id='username' placeholder='Username'>
<textarea id='message'></textarea>
<button onclick='sendMessage()'>Send</button>
</div>
<div class='ai-panel'>
<div class='card'>
<h3>AI Assistant</h3>
<p>Multi-provider orchestration active</p>
</div>
<div class='card'>
<h3>Observability</h3>
<p>Prometheus telemetry connected</p>
</div>
<div class='card'>
<h3>Vector Memory</h3>
<p>Semantic retrieval online</p>
</div>
</div>
</div>
<script>
const ws = new WebSocket(`ws://${location.host}/ws/global`)

ws.onmessage = function(event) {
    const payload = JSON.parse(event.data)
    const messages = document.getElementById('messages')

    messages.innerHTML += `
        <div class='message'>
            <b>${payload.username || 'SYSTEM'}</b><br>
            ${payload.message}<br>
            <small>${payload.timestamp}</small>
        </div>
    `
}

function sendMessage() {
    const username = document.getElementById('username').value
    const message = document.getElementById('message').value

    ws.send(JSON.stringify({
        username,
        message,
        room: 'global'
    }))
}
</script>
</body>
</html>
'''


@app.on_event('startup')
async def startup_event():
    await platform.bootstrap()


@app.get('/')
async def dashboard():
    return HTMLResponse(DASHBOARD_HTML)


@app.get('/health')
async def health_check():
    health = await platform.system_health()

    return {
        'status': 'healthy',
        'timestamp': str(datetime.utcnow()),
        'platform': health
    }


@app.websocket('/ws/{room}')
async def websocket_gateway(websocket: WebSocket, room: str):
    username = f'user-{uuid.uuid4()}'

    await manager.connect(websocket, username)
    await manager.register_room_member(room, username)

    await manager.broadcast_global({
        'type': 'system',
        'message': f'{username} connected to {room}',
        'timestamp': str(datetime.utcnow())
    })

    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)

            message = payload.get('message', '')
            sender = payload.get('username', username)

            injection = manager_guardrails.detect_prompt_injection(message)

            if injection:
                await manager.send_personal(sender, {
                    'type': 'security',
                    'message': 'Prompt injection detected',
                    'timestamp': str(datetime.utcnow())
                })
                continue

            await workspace_state.add_audit_log(
                action='chat-message',
                actor=sender
            )

            await semantic_memory.store_memory(message)

            ai_response = await platform.process_objective(message)

            await manager.room_broadcast(room, {
                'type': 'chat',
                'username': sender,
                'message': message,
                'timestamp': str(datetime.utcnow()),
                'ai': ai_response['llm_response']
            })

    except WebSocketDisconnect:
        await manager.disconnect(username)

        await manager.broadcast_global({
            'type': 'system',
            'message': f'{username} disconnected',
            'timestamp': str(datetime.utcnow())
        })


@app.post('/api/objectives/process')
async def process_objective(request: ObjectiveRequest):
    result = await platform.process_objective(request.objective)

    return JSONResponse(content=result)


@app.post('/api/security/threat-intel')
async def threat_intelligence(request: ThreatRequest):
    result = await intel_engine.fetch_iocs(request.indicator)

    return JSONResponse(content=result)


@app.post('/api/security/siem')
async def siem_ingestion(request: ThreatRequest):
    result = await siem_pipeline.ingest_event({
        'indicator': request.indicator,
        'timestamp': str(datetime.utcnow())
    })

    return JSONResponse(content=result)


@app.post('/api/security/analyze')
async def analyze_security(request: ThreatRequest):
    result = await platform.security_pipeline(request.indicator)

    return JSONResponse(content=result)


@app.post('/api/execution/python')
async def execute_python(request: SandboxRequest):
    result = await execution_sandbox.execute_python(request.code)

    return JSONResponse(content=result)


@app.post('/api/execution/bash')
async def execute_bash(request: SandboxRequest):
    result = await execution_sandbox.execute_bash(request.code)

    return JSONResponse(content=result)


@app.post('/api/agents/create')
async def create_agent(request: AgentRequest):
    result = await platform.agent_coordinator.register_agent(
        request.name,
        request.objective
    )

    return JSONResponse(content=result)


@app.get('/api/agents/health')
async def agents_health():
    result = await platform.agent_coordinator.health_report()

    return JSONResponse(content=result)


@app.post('/api/goals/create')
async def create_goal(request: ObjectiveRequest):
    goal_id = str(uuid.uuid4())

    result = await goal_engine.register_goal(
        goal_id,
        request.objective
    )

    return {
        'goal_id': goal_id,
        'goal': result
    }


@app.post('/api/memory/store')
async def store_memory(request: KnowledgeRequest):
    result = await semantic_memory.store_memory(request.query)

    return result


@app.post('/api/memory/search')
async def search_memory(request: KnowledgeRequest):
    result = await semantic_memory.retrieve_similar(request.query)

    return {
        'results': result
    }


@app.get('/api/workspace/state')
async def workspace_metrics():
    return {
        'rooms': workspace_state.rooms,
        'audit_logs': workspace_state.audit_logs[-20:],
        'active_connections': len(manager.connections),
        'timestamp': str(datetime.utcnow())
    }


@app.post('/api/upload')
async def upload_file(file: UploadFile = File(...)):
    os.makedirs('uploads', exist_ok=True)

    path = f'uploads/{file.filename}'

    with open(path, 'wb') as f:
        f.write(await file.read())

    return {
        'status': 'uploaded',
        'filename': file.filename,
        'path': path
    }


@app.get('/api/telemetry')
async def telemetry_dashboard():
    return {
        'active_agents': len(platform.agent_coordinator.agents),
        'queued_tasks': len(platform.task_queue.queue),
        'workspace_tabs': len(platform.workspace.active_tabs),
        'memory_objects': len(platform.memory_manager.long_term_memory),
        'timestamp': str(datetime.utcnow())
    }


@app.get('/api/platform/status')
async def platform_status():
    return {
        'platform': 'AIOS',
        'version': '4.0.0',
        'modules': {
            'autonomous_agents': True,
            'rag_pipeline': True,
            'vector_memory': True,
            'observability': True,
            'cybersecurity_ai': True,
            'distributed_execution': True,
            'kubernetes_ready': True,
            'langchain_enabled': True
        },
        'providers': [
            'openai',
            'ollama',
            'groq',
            'huggingface'
        ]
    }


@app.get('/api/docs/system')
async def system_documentation():
    return {
        'architecture': 'enterprise-ai-operating-system',
        'components': [
            'agent-orchestrator',
            'vector-memory',
            'rag-engine',
            'sandbox-runtime',
            'telemetry-stack',
            'distributed-event-bus',
            'multi-provider-llm-gateway'
        ],
        'capabilities': [
            'autonomous-planning',
            'semantic-memory',
            'threat-intelligence',
            'siem-analysis',
            'multi-agent-execution',
            'realtime-collaboration'
        ]
    }
