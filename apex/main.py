"""APEX Main Application Entry Point"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from collections import deque
from datetime import datetime, timezone
from typing import Any
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

SYSTEM = "APEX-AI-ENGINE"
ROLE = "commerce_engine"
VERSION = "1.0.0"
CONTRACT_VERSION = "1.0.0"

_events: deque[dict[str, Any]] = deque(maxlen=1000)
_counters: dict[str, int] = {
    "requests_total": 0,
    "health_checks": 0,
    "meta_checks": 0,
    "events_checks": 0,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("apex.startup", version="1.0.0", company="Garcar Enterprise")
    try:
        await init_db()
    except Exception as exc:
        log.error("apex.db_init_skipped", error=str(exc))
    try:
        await orchestrator.start()
    except Exception as exc:
        log.error("apex.orchestrator_start_failed", error=str(exc))
    yield
    try:
        await orchestrator.shutdown()
    except Exception:
        pass
    log.info("apex.shutdown")


app = FastAPI(
    title="APEX AI Engine",
    description="Autonomous Profit & Enterprise eXecution Engine — Garcar Enterprise",
    version=VERSION,
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

# Metrics (Prometheus text at /metrics — Garcar Base Contract accepts this)
setup_metrics(app)

# Routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    _counters["health_checks"] += 1
    _counters["requests_total"] += 1
    return {
        "status": "operational",
        "system": SYSTEM,
        "version": VERSION,
        "timestamp": _now(),
        "engine": "APEX",
        "company": "Garcar Enterprise",
    }


@app.get("/meta")
async def meta():
    """Garcar Base Contract discovery endpoint."""
    _counters["meta_checks"] += 1
    _counters["requests_total"] += 1
    return {
        "system": SYSTEM,
        "role": ROLE,
        "contract_version": CONTRACT_VERSION,
        "endpoints": ["/health", "/meta", "/metrics", "/events"],
        "event_bus_topic_schema": "garcar.{system}.{event_type}",
    }


@app.get("/events")
async def events():
    """In-memory event ring until external bus is wired."""
    _counters["events_checks"] += 1
    _counters["requests_total"] += 1
    ev = list(_events)
    return {"events": ev, "total": len(ev)}


@app.get("/contract/metrics")
async def contract_metrics_json():
    """JSON counters companion to Prometheus /metrics."""
    return dict(_counters)


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
