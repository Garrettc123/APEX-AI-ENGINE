"""Webhook Endpoints — Stripe, GitHub, Notion"""
import hashlib
import hmac
from fastapi import APIRouter, Request, HTTPException
from apex.config import settings
import structlog

log = structlog.get_logger()
router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
        except Exception as e:
            raise HTTPException(400, f"Webhook error: {e}")
    else:
        import orjson
        event = orjson.loads(payload)

    event_type = event.get("type", "")
    log.info("webhook.stripe", event_type=event_type)

    handlers = {
        "checkout.session.completed": _handle_checkout_completed,
        "invoice.paid": _handle_invoice_paid,
        "customer.subscription.deleted": _handle_subscription_cancelled,
    }

    handler = handlers.get(event_type)
    if handler:
        await handler(event)

    return {"received": True}


async def _handle_checkout_completed(event: dict):
    session = event["data"]["object"]
    log.info("stripe.checkout.completed", session_id=session.get("id"))


async def _handle_invoice_paid(event: dict):
    invoice = event["data"]["object"]
    log.info("stripe.invoice.paid", invoice_id=invoice.get("id"), amount=invoice.get("amount_paid"))


async def _handle_subscription_cancelled(event: dict):
    sub = event["data"]["object"]
    log.info("stripe.subscription.cancelled", sub_id=sub.get("id"))


@router.post("/github")
async def github_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")

    if settings.GITHUB_WEBHOOK_SECRET:
        expected = "sha256=" + hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise HTTPException(401, "Invalid signature")

    event = request.headers.get("X-GitHub-Event", "")
    log.info("webhook.github", event=event)
    return {"received": True}
