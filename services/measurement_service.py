from datetime import datetime

from database.connection import get_connection
from services.validation_service import validate_measurement


def save_measurement(sensor_id: int, temperature: float, humidity: float):

    valid, message = validate_measurement(temperature, humidity)

    if not valid:
        raise ValueError(message)

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO measurements(
            sensor_id,
            temperature,
            humidity,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (sensor_id, temperature, humidity, datetime.now()),
    )

    conn.commit()
    conn.close()
