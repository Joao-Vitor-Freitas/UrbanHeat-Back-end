from database.connection import get_connection
from services.heatscore_service import get_heatscore_by_region


def get_dashboard() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM regions ORDER BY name")
    regions = cur.fetchall()

    cur.execute(
        """
        SELECT s.region_id, m.temperature, m.humidity, m.created_at
        FROM measurements m
        JOIN sensors s ON s.id = m.sensor_id
        WHERE m.id IN (
            SELECT MAX(id) FROM measurements GROUP BY sensor_id
        )
        """
    )
    latest_by_region = {}
    for row in cur.fetchall():
        region_id = row[0]
        if region_id not in latest_by_region:
            latest_by_region[region_id] = {
                "temperature": row[1],
                "humidity": row[2],
                "last_measurement": row[3],
            }

    conn.close()

    result = []
    for region_id, region_name in regions:
        heatscore = get_heatscore_by_region(region_id)
        latest = latest_by_region.get(region_id)
        result.append(
            {
                "region_id": region_id,
                "region_name": region_name,
                "current_temperature": latest["temperature"] if latest else None,
                "current_humidity": latest["humidity"] if latest else None,
                "last_measurement": latest["last_measurement"] if latest else None,
                "heatscore": heatscore,
            }
        )

    return result
