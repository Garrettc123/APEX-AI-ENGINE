"""APEX Main Application Entry Point"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import structlog
import orjson

from apex.config import settings
from apex.db.database import init_db
from apex.api.router import api_router
from apex.core.orchestrator import ApexOrchestrator
from apex.core.connection_manager import ConnectionManager
from apex.monitoring.metrics import setup_metrics

log = structlog.get_logger()
manager = ConnectionManager()
orchestrator = ApexOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("apex.startup", version="1.0.0", company="Garcar Enterprise")
    await init_db()
    await orchestrator.start()
    yield
    await orchestrator.shutdown()
    log.info("apex.shutdown")


app = FastAPI(
    title="APEX AI Engine",
    description="Autonomous Profit & Enterprise eXecution Engine — Garcar Enterprise",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
setup_metrics(app)

# Routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "operational", "engine": "APEX", "version": "1.0.0", "company": "Garcar Enterprise"}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """APEX Live Dashboard"""
    with open("apex/templates/dashboard.html") as f:
        return HTMLResponse(content=f.read())


@app.websocket("/ws/agents")
async def websocket_agents(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = orjson.loads(data)
            if payload.get("type") == "ping":
                await websocket.send_text(orjson.dumps({"type": "pong"}).decode())
            await manager.broadcast(orjson.dumps({"type": "echo", "data": payload}).decode())
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/revenue")
async def websocket_revenue(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            snapshot = await orchestrator.get_revenue_snapshot()
            await websocket.send_text(orjson.dumps(snapshot).decode())
            import asyncio
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
