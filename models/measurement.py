from dataclasses import dataclass
from datetime import datetime


@dataclass
class Measurement:
    id: int | None
    sensor_code: str
    temperature: float
    humidity: float
    created_at: datetime
