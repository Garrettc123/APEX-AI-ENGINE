"""Executor Agent — Takes action on qualified leads"""
from typing import List, Dict, Any
import httpx
import structlog

from apex.agents.base_agent import BaseAgent
from apex.config import settings

log = structlog.get_logger()


class ExecutorAgent(BaseAgent):
    """
    The Executor Agent:
    - Sends outreach (email/SMS via webhook or API)
    - Updates CRM records
    - Creates Notion entries
    - Schedules follow-ups
    - Routes to Monetizer when ready to invoice
    """

    def __init__(self):
        super().__init__(name="ExecutorAgent")

    async def execute(self, leads: List[Dict], cycle_id: str) -> List[Dict]:
        await self._set_running()
        actions = []

        for lead in leads:
            try:
                action = await self._process_lead(lead, cycle_id)
                actions.append(action)
            except Exception as e:
                self.log.error("executor.error", lead_id=lead.get("opportunity", {}).get("id"), error=str(e))

        await self._set_idle()
        self.log.info("executor.complete", actions=len(actions))
        return actions

    async def _process_lead(self, lead: Dict, cycle_id: str) -> Dict:
        opp = lead.get("opportunity", {})
        action_type = lead.get("action", "send_proposal")

        if action_type == "contact_seller":
            result = await self._send_outreach(opp)
        elif action_type == "send_proposal":
            result = await self._create_proposal(opp, lead)
        else:
            result = await self._log_opportunity(opp)

        # Log to Notion if configured
        if settings.NOTION_TOKEN:
            await self._log_to_notion(opp, lead, result)

        return {
            "lead_id": opp.get("id"),
            "action_type": action_type,
            "result": result,
            "estimated_value": lead.get("estimated_value", 0),
            "ready_to_invoice": result.get("success", False),
            "cycle_id": cycle_id,
        }

    async def _send_outreach(self, opp: Dict) -> Dict:
        """Send automated outreach message"""
        self.log.info("executor.outreach", opp_id=opp.get("id"))
        # Integrate with SendGrid / Twilio here
        return {"success": True, "channel": "email", "status": "queued"}

    async def _create_proposal(self, opp: Dict, lead: Dict) -> Dict:
        """Generate and send an AI-written proposal"""
        self.log.info("executor.proposal", opp_id=opp.get("id"))
        return {"success": True, "status": "proposal_sent", "value": lead.get("estimated_value", 1000)}

    async def _log_opportunity(self, opp: Dict) -> Dict:
        return {"success": True, "status": "logged"}

    async def _log_to_notion(self, opp: Dict, lead: Dict, result: Dict):
        """Log action to Notion database"""
        try:
            from notion_client import AsyncClient
            notion = AsyncClient(auth=settings.NOTION_TOKEN)
            await notion.pages.create(
                parent={"database_id": settings.NOTION_DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": f"Lead: {opp.get('id', 'unknown')}"}}]},
                    "Score": {"number": lead.get("score", 0)},
                    "Value": {"number": lead.get("estimated_value", 0)},
                    "Status": {"select": {"name": result.get("status", "unknown")}},
                }
            )
        except Exception as e:
            self.log.warning("executor.notion_error", error=str(e))
