from database.connection import get_connection


def create_sensor(sensor_code: str, region_id: int):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO sensors(sensor_code, region_id)
        VALUES (?, ?)
        """,
        (sensor_code, region_id),
    )
    conn.commit()
    conn.close()


def get_sensor_by_code(sensor_code: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, sensor_code, region_id
        FROM sensors
        WHERE sensor_code = ?
        """,
        (sensor_code,),
    )
    sensor = cur.fetchone()
    conn.close()
    return sensor


def get_sensors_by_region(region_id: int) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, sensor_code, region_id
        FROM sensors
        WHERE region_id = ?
        ORDER BY sensor_code
        """,
        (region_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "sensor_code": r[1], "region_id": r[2]} for r in rows]


def get_all_sensors() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.id, s.sensor_code, s.region_id, r.name
        FROM sensors s
        JOIN regions r ON r.id = s.region_id
        ORDER BY r.name, s.sensor_code
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "sensor_code": r[1], "region_id": r[2], "region_name": r[3]}
        for r in rows
    ]
