"""
Visual Psychology endpoint — delegates to the main visual.py module
for all 10 scenarios with per-user randomization.
"""
from fastapi import APIRouter, Query
from app.api.endpoints.visual import get_visual_scenarios as _get_scenarios

router = APIRouter()


@router.get("/scenarios")
async def get_visual_scenarios(
    user_id: str = Query("anonymous", description="User ID for per-user randomization"),
    count: int = Query(5, ge=3, le=10, description="Number of scenarios to return")
):
    """Proxy to the main visual scenarios endpoint with per-user randomization."""
    return await _get_scenarios(user_id=user_id, count=count)
