"""APEX API Router — All REST endpoints"""
from fastapi import APIRouter
from apex.api.endpoints import agents, revenue, leads, webhooks, auth, subscriptions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(revenue.router, prefix="/revenue", tags=["Revenue"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
