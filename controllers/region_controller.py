from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.region_service import create_region, get_regions

router = APIRouter(prefix="/regions", tags=["Regions"])


class RegionInput(BaseModel):
    name: str


@router.post("/", status_code=201)
def create(body: RegionInput):
    try:
        create_region(body.name)
        return {"message": "Region created successfully", "name": body.name}
    except Exception:
        raise HTTPException(status_code=409, detail="Region already exists")


@router.get("/")
def list_regions():
    regions = get_regions()
    return [{"id": r[0], "name": r[1]} for r in regions]
