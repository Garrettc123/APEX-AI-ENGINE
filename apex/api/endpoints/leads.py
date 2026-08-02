"""Lead Management Endpoints"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_leads():
    return {"leads": [], "message": "Connect to Supabase to list leads"}


@router.get("/count")
async def lead_count():
    return {"total": 0, "qualified": 0, "converted": 0}
