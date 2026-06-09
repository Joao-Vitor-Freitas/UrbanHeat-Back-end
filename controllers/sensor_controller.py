from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.sensor_service import (
    create_sensor,
    get_sensor_by_code,
    get_sensors_by_region,
    get_all_sensors,
)

router = APIRouter(prefix="/sensors", tags=["Sensors"])


class SensorInput(BaseModel):
    sensor_code: str
    region_id: int


@router.post("/", status_code=201)
def create(body: SensorInput):
    try:
        create_sensor(body.sensor_code, body.region_id)
        return {
            "message": "Sensor created successfully",
            "sensor_code": body.sensor_code,
            "region_id": body.region_id,
        }
    except Exception:
        raise HTTPException(status_code=409, detail="Sensor already exists")


@router.get("/")
def list_sensors():
    return get_all_sensors()


@router.get("/region/{region_id}")
def list_by_region(region_id: int):
    sensors = get_sensors_by_region(region_id)
    if not sensors:
        raise HTTPException(status_code=404, detail="No sensors found for this region")
    return sensors


@router.get("/{sensor_code}")
def get_sensor(sensor_code: str):
    sensor = get_sensor_by_code(sensor_code)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return {"id": sensor[0], "sensor_code": sensor[1], "region_id": sensor[2]}
