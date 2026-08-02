"""Agent Management Endpoints"""
from fastapi import APIRouter, Depends
from apex.api.deps import get_current_user

router = APIRouter()


@router.get("/status")
async def get_agent_statuses():
    """Get status of all four APEX agents"""
    from apex.main import orchestrator
    return {"agents": orchestrator.get_agent_statuses()}


@router.post("/trigger")
async def trigger_pipeline(user=Depends(get_current_user)):
    """Manually trigger a full pipeline cycle"""
    from apex.main import orchestrator
    result = await orchestrator.trigger_manual_cycle()
    return result


@router.get("/metrics")
async def get_metrics():
    """Get system-wide metrics"""
    from apex.main import orchestrator
    return await orchestrator.get_revenue_snapshot()
