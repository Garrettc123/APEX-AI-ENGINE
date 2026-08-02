"""Base Agent — All APEX agents inherit from this"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime
from enum import Enum
import structlog

log = structlog.get_logger()


class AgentState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    PAUSED = "paused"


class BaseAgent(ABC):
    """
    Abstract base for all APEX agents.
    Provides: logging, state tracking, retry logic, metrics collection.
    """

    def __init__(self, name: str):
        self.name = name
        self.state = AgentState.IDLE
        self.last_run: datetime | None = None
        self.run_count = 0
        self.error_count = 0
        self.log = structlog.get_logger(agent=name)

    def status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "error_count": self.error_count,
        }

    async def _set_running(self):
        self.state = AgentState.RUNNING
        self.last_run = datetime.utcnow()
        self.run_count += 1

    async def _set_idle(self):
        self.state = AgentState.IDLE

    async def _set_error(self, error: str):
        self.state = AgentState.ERROR
        self.error_count += 1
        self.log.error("agent.error", error=error)
