"""Subscription Management Endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from apex.config import settings

router = APIRouter()


class CheckoutRequest(BaseModel):
    tier: str  # starter | pro | enterprise
    success_url: str
    cancel_url: str


@router.post("/checkout")
async def create_checkout(req: CheckoutRequest):
    price_map = {
        "starter": settings.STRIPE_PRICE_ID_STARTER,
        "pro": settings.STRIPE_PRICE_ID_PRO,
        "enterprise": settings.STRIPE_PRICE_ID_ENTERPRISE,
    }
    price_id = price_map.get(req.tier)
    if not price_id:
        raise HTTPException(400, "Invalid tier")

    from apex.agents.monetizer import MonetizerAgent
    m = MonetizerAgent()
    url = await m.create_checkout_session(price_id, req.success_url, req.cancel_url)
    return {"checkout_url": url}


@router.get("/tiers")
async def get_tiers():
    return {
        "tiers": [
            {"id": "starter", "name": "Starter", "price": 97, "features": ["5 agents", "1K leads/mo", "Basic analytics"]},
            {"id": "pro", "name": "Pro", "price": 297, "features": ["20 agents", "10K leads/mo", "Full analytics", "MARS API"]},
            {"id": "enterprise", "name": "Enterprise", "price": 997, "features": ["Unlimited agents", "Unlimited leads", "White-label", "Custom integrations"]},
        ]
    }
