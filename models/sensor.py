from dataclasses import dataclass


@dataclass
class Sensor:
    id: int | None
    sensor_code: str
    region_id: int
