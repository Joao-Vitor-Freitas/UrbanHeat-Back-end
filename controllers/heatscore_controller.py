from fastapi import APIRouter, HTTPException
from services.heatscore_service import (
    save_heatscore,
    get_heatscore_by_region,
    get_heatscore_history,
    get_ranking,
)

router = APIRouter(prefix="/heatscore", tags=["HeatScore"])


@router.post("/regions/{region_id}/calculate", status_code=201)
def calculate(region_id: int):
    try:
        data = save_heatscore(region_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions/{region_id}")
def current(region_id: int):
    data = get_heatscore_by_region(region_id)
    if not data:
        raise HTTPException(
            status_code=404, detail="No HeatScore found for this region"
        )
    return data


@router.get("/regions/{region_id}/history")
def history(region_id: int):
    data = get_heatscore_history(region_id)
    if not data:
        raise HTTPException(
            status_code=404, detail="No HeatScore history found for this region"
        )
    return data


@router.get("/ranking")
def ranking():
    data = get_ranking()
    return data
