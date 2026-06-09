from dataclasses import dataclass
from datetime import datetime


@dataclass
class HeatScore:
    id: int | None
    region_id: int
    score: float
    classification: str
    average_temperature: float
    high_temperature_frequency: float
    critical_duration: float
    calculated_at: datetime
