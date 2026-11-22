"""Executor Agent — approval-bound plan preparation only.

This worker does not send email, SMS, offers, create CRM rows or invoice buyers.
External actions require a separate approved and auditable dispatch integration.
"""
from typing import List, Dict
import structlog
from apex.agents.base_agent import BaseAgent

log = structlog.get_logger()


class ExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ExecutorAgent")

    async def execute(self, leads: List[Dict], cycle_id: str) -> List[Dict]:
        await self._set_running()
        actions = []
        try:
            for lead in leads:
                opp = lead.get("opportunity") or {}
                # Even a misleading model action cannot override approval gates.
                actions.append({
                    "lead_id": opp.get("id"),
                    "action_type": "research_only",
                    "result": {"success": False, "status": "approval_required",
                               "outbound_sent": False, "deal_closed": False},
                    "estimated_value": None,
                    "ready_to_invoice": False,
                    "cycle_id": cycle_id,
                })
        finally:
            await self._set_idle()
        self.log.info("executor.review_queue_only", count=len(actions), cycle_id=cycle_id)
        return actions
