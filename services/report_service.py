import csv
import io
from database.connection import get_connection
from services.heatscore_service import get_heatscore_by_region, get_ranking


def get_critical_regions_report() -> list[dict]:
    ranking = get_ranking()
    return [r for r in ranking if r["score"] >= 75]


def get_historical_report(region_id: int) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.name, m.temperature, m.humidity, m.created_at
        FROM measurements m
        JOIN sensors s ON s.id = m.sensor_id
        JOIN regions r ON r.id = s.region_id
        WHERE s.region_id = ?
          AND m.created_at >= datetime('now', '-30 days')
        ORDER BY m.created_at DESC
        """,
        (region_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "region_name": r[0],
            "temperature": r[1],
            "humidity": r[2],
            "created_at": r[3],
        }
        for r in rows
    ]


def export_csv(region_id: int | None = None) -> tuple[str, str]:
    conn = get_connection()
    cur = conn.cursor()

    if region_id:
        cur.execute(
            """
            SELECT r.name, m.temperature, m.humidity, m.created_at
            FROM measurements m
            JOIN sensors s ON s.id = m.sensor_id
            JOIN regions r ON r.id = s.region_id
            WHERE s.region_id = ?
              AND m.created_at >= datetime('now', '-30 days')
            ORDER BY r.name, m.created_at DESC
            """,
            (region_id,),
        )
    else:
        cur.execute(
            """
            SELECT r.name, m.temperature, m.humidity, m.created_at
            FROM measurements m
            JOIN sensors s ON s.id = m.sensor_id
            JOIN regions r ON r.id = s.region_id
            WHERE m.created_at >= datetime('now', '-30 days')
            ORDER BY r.name, m.created_at DESC
            """
        )

    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["region", "temperature", "humidity", "created_at"])
    writer.writerows(rows)

    return output.getvalue(), "measurements.csv"


def export_critical_csv() -> tuple[str, str]:
    critical = get_critical_regions_report()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "region_name",
            "score",
            "classification",
            "average_temperature",
            "high_temperature_frequency",
            "critical_duration",
            "created_at",
        ]
    )
    for r in critical:
        writer.writerow(
            [
                r["region_name"],
                r["score"],
                r["classification"],
                r["average_temperature"],
                r["high_temperature_frequency"],
                r["critical_duration"],
                r["created_at"],
            ]
        )

    return output.getvalue(), "critical_regions.csv"
