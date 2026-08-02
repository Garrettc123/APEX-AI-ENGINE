"""Revenue & Financial Endpoints"""
from fastapi import APIRouter, Depends
from apex.api.deps import get_current_user

router = APIRouter()


@router.get("/snapshot")
async def revenue_snapshot():
    from apex.main import orchestrator
    return await orchestrator.get_revenue_snapshot()


@router.get("/history")
async def revenue_history():
    from apex.main import orchestrator
    return {"history": orchestrator.metrics.cycle_history[-50:]}
