"""APEX Core Orchestrator — Brain of the entire system"""
import asyncio
from typing import Dict, Any, List
import structlog
from datetime import datetime

from apex.agents.scout import ScoutAgent
from apex.agents.analyst import AnalystAgent
from apex.agents.executor import ExecutorAgent
from apex.agents.monetizer import MonetizerAgent
from apex.db.models import AgentStatus, SystemMetrics

log = structlog.get_logger()


class ApexOrchestrator:
    """
    The APEX Orchestrator coordinates all four agent types:
    Scout → Analyst → Executor → Monetizer
    
    Each stage feeds outputs as inputs to the next.
    The orchestrator manages lifecycle, health, and inter-agent messaging.
    """

    def __init__(self):
        self.scout = ScoutAgent()
        self.analyst = AnalystAgent()
        self.executor = ExecutorAgent()
        self.monetizer = MonetizerAgent()
        self.active = False
        self.metrics: SystemMetrics = SystemMetrics()
        self._pipeline_task = None

    async def start(self):
        log.info("orchestrator.start")
        self.active = True
        self._pipeline_task = asyncio.create_task(self._run_pipeline_loop())

    async def shutdown(self):
        log.info("orchestrator.shutdown")
        self.active = False
        if self._pipeline_task:
            self._pipeline_task.cancel()

    async def _run_pipeline_loop(self):
        """
        Continuous autonomous pipeline loop:
        Every 60 seconds, trigger full Scout → Analyst → Executor → Monetizer cycle
        """
        while self.active:
            try:
                await self._execute_pipeline_cycle()
                await asyncio.sleep(60)  # Configurable interval
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error("pipeline.error", error=str(e))
                await asyncio.sleep(10)  # Back off on error

    async def _execute_pipeline_cycle(self):
        cycle_id = f"cycle-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        log.info("pipeline.cycle.start", cycle_id=cycle_id)

        # Stage 1: Scout discovers opportunities
        opportunities = await self.scout.discover(cycle_id=cycle_id)
        log.info("scout.done", count=len(opportunities), cycle_id=cycle_id)

        if not opportunities:
            log.info("pipeline.no_opportunities", cycle_id=cycle_id)
            return

        # Stage 2: Analyst qualifies and scores
        qualified = await self.analyst.qualify(opportunities=opportunities, cycle_id=cycle_id)
        log.info("analyst.done", qualified=len(qualified), cycle_id=cycle_id)

        if not qualified:
            return

        # Stage 3: Executor initiates outreach / action
        actions = await self.executor.execute(leads=qualified, cycle_id=cycle_id)
        log.info("executor.done", actions=len(actions), cycle_id=cycle_id)

        # Stage 4: Monetizer handles payments / invoicing
        revenue = await self.monetizer.monetize(actions=actions, cycle_id=cycle_id)
        log.info("monetizer.done", revenue=revenue, cycle_id=cycle_id)

        self.metrics.record_cycle(
            cycle_id=cycle_id,
            opportunities=len(opportunities),
            qualified=len(qualified),
            actions=len(actions),
            revenue=revenue,
        )

    async def get_revenue_snapshot(self) -> Dict[str, Any]:
        return {
            "type": "revenue_snapshot",
            "timestamp": datetime.utcnow().isoformat(),
            "total_revenue": self.metrics.total_revenue,
            "cycles_completed": self.metrics.cycles_completed,
            "leads_discovered": self.metrics.total_leads,
            "deals_closed": self.metrics.deals_closed,
            "active_subscriptions": self.metrics.active_subscriptions,
        }

    async def trigger_manual_cycle(self) -> Dict[str, Any]:
        """API-triggered manual pipeline run"""
        asyncio.create_task(self._execute_pipeline_cycle())
        return {"status": "triggered", "message": "Pipeline cycle initiated"}

    def get_agent_statuses(self) -> List[Dict]:
        return [
            self.scout.status(),
            self.analyst.status(),
            self.executor.status(),
            self.monetizer.status(),
        ]
