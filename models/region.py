from dataclasses import dataclass


@dataclass
class Region:
    id: int | None
    name: str
