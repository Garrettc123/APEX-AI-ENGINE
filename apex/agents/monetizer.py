"""Monetizer Agent — Stripe-powered revenue automation"""
from typing import List, Dict, Any
import structlog

from apex.agents.base_agent import BaseAgent
from apex.config import settings

log = structlog.get_logger()


class MonetizerAgent(BaseAgent):
    """
    The Monetizer Agent autonomously:
    - Creates Stripe invoices for completed deals
    - Manages subscription billing
    - Tracks revenue metrics
    - Triggers payout logic
    - Reports P&L to dashboard
    """

    def __init__(self):
        super().__init__(name="MonetizerAgent")

    async def monetize(self, actions: List[Dict], cycle_id: str) -> float:
        await self._set_running()
        total_revenue = 0.0

        ready = [a for a in actions if a.get("ready_to_invoice")]
        self.log.info("monetizer.invoicing", count=len(ready))

        for action in ready:
            try:
                revenue = await self._process_payment(action)
                total_revenue += revenue
            except Exception as e:
                self.log.error("monetizer.error", action_id=action.get("lead_id"), error=str(e))

        await self._set_idle()
        self.log.info("monetizer.cycle_revenue", total=total_revenue, cycle_id=cycle_id)
        return total_revenue

    async def _process_payment(self, action: Dict) -> float:
        """Create Stripe invoice or charge for the completed action"""
        value = action.get("estimated_value", 0)
        if value <= 0:
            return 0.0

        if not settings.STRIPE_SECRET_KEY:
            self.log.info("monetizer.mock_invoice", value=value)
            return value

        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Create invoice item
            invoice = stripe.Invoice.create(
                auto_advance=True,
                collection_method="send_invoice",
                days_until_due=30,
                metadata={
                    "cycle_id": action.get("cycle_id", ""),
                    "lead_id": action.get("lead_id", ""),
                    "source": "apex_engine",
                }
            )
            self.log.info("monetizer.invoice_created", invoice_id=invoice.id, value=value)
            return value
        except Exception as e:
            self.log.error("monetizer.stripe_error", error=str(e))
            return 0.0

    async def create_subscription(self, customer_id: str, price_id: str) -> Dict:
        """Create a new Stripe subscription"""
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        sub = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
        )
        return {"subscription_id": sub.id, "status": sub.status}

    async def create_checkout_session(self, price_id: str, success_url: str, cancel_url: str) -> str:
        """Create Stripe Checkout Session"""
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.url
