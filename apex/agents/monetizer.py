"""Monetizer Agent — no synthetic revenue or unapproved billing.

Reconciliation requires provider-verified settled transactions; not estimates,
invoice creation, or agent-completion statuses.
"""
from typing import List, Dict
import structlog
from apex.agents.base_agent import BaseAgent

log = structlog.get_logger()


class MonetizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MonetizerAgent")

    async def monetize(self, actions: List[Dict], cycle_id: str) -> float:
        await self._set_running()
        try:
            # Never treat a proposed price, invoice or checkout as received cash.
            self.log.info("monetizer.settlement_unverified", count=len(actions),
                          cycle_id=cycle_id, recorded_revenue=0)
            return 0.0
        finally:
            await self._set_idle()

    async def _process_payment(self, action: Dict) -> float:
        # An internal agent cannot bill anyone via this method.
        return 0.0

    async def create_subscription(self, customer_id: str, price_id: str) -> Dict:
        raise PermissionError("Subscriptions require separate payment authorization and provider reconciliation.")

    async def create_checkout_session(self, price_id: str, success_url: str, cancel_url: str) -> str:
        raise PermissionError("Checkout creation requires a separate approved integration.")
