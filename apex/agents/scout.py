"""Scout Agent — bounded source-backed opportunity research.

Real-estate discovery consumes verified listing research only. This module
does not invent public records, infer vacant-house occupancy, or send outreach.
"""
from typing import List, Dict, Any
import structlog
from apex.agents.base_agent import BaseAgent
from apex.agents.property_feed import load_property_feed

log = structlog.get_logger()


class ScoutAgent(BaseAgent):
    """Return observed real-estate candidates, never mock properties or sellers."""

    def __init__(self):
        super().__init__(name="ScoutAgent")
        self.sources = [self._scan_verified_properties]

    async def discover(self, cycle_id: str) -> List[Dict[str, Any]]:
        await self._set_running()
        opportunities = []
        try:
            for source_fn in self.sources:
                try:
                    results = await source_fn(cycle_id=cycle_id)
                    opportunities.extend(results)
                    self.log.info("scout.source.done", source=source_fn.__name__, found=len(results))
                except Exception as exc:
                    self.log.warning("scout.source.unavailable", source=source_fn.__name__, error=type(exc).__name__)
        finally:
            await self._set_idle()
        self.log.info("scout.total", opportunities=len(opportunities), cycle_id=cycle_id)
        return opportunities

    async def _scan_verified_properties(self, cycle_id: str) -> List[Dict]:
        rows = load_property_feed()
        return [{
            "id": row["id"],
            "type": "real_estate",
            "source": "public_listing_verified_research",
            "data": row,
            "cycle_id": cycle_id,
            "research_only": True,
            "authorized_for_outreach": False,
            "seller_contract_verified": False,
            "buyer_commitment_verified": False,
        } for row in rows]
