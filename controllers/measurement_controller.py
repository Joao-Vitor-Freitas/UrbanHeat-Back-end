from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from services.measurement_service import save_measurement
from services.sensor_service import get_sensor_by_code
from database.connection import get_connection

router = APIRouter(prefix="/measurements", tags=["Measurements"])


class MeasurementInput(BaseModel):
    sensor_code: str
    temperature: float
    humidity: float


@router.post("/", status_code=201)
def receive(body: MeasurementInput):
    sensor = get_sensor_by_code(body.sensor_code)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    try:
        save_measurement(sensor[0], body.temperature, body.humidity)
        return {
            "message": "Measurement saved",
            "sensor_code": body.sensor_code,
            "temperature": body.temperature,
            "humidity": body.humidity,
            "created_at": datetime.now().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/regions/{region_id}")
def history(region_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT m.id, s.sensor_code, m.temperature, m.humidity, m.created_at
        FROM measurements m
        JOIN sensors s ON s.id = m.sensor_id
        WHERE s.region_id = ?
          AND m.created_at >= datetime('now', '-30 days')
        ORDER BY m.created_at DESC
        """,
        (region_id,),
    )
    rows = cur.fetchall()
    conn.close()
    if not rows:
        raise HTTPException(
            status_code=404, detail="No measurements found for this region"
        )
    return [
        {
            "id": r[0],
            "sensor_code": r[1],
            "temperature": r[2],
            "humidity": r[3],
            "created_at": r[4],
        }
        for r in rows
    ]
