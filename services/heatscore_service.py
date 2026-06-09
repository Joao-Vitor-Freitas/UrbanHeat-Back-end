from datetime import datetime
from database.connection import get_connection


# ─────────────────────────────────────────────────────────────
# Fórmula do HeatScore (escala 0–100, RN-11)
# Janela: últimos 30 dias de medições (RN-24)
#
# Componentes (RN-10):
#   Temperatura média       → peso 40  | (avg_temp / 50) * 40
#   Frequência de calor     → peso 30  | (leituras >= 35°C / total) * 30
#   Permanência crítica     → peso 20  | (horas >= 35°C / horas totais) * 20
#   Penalidade de umidade   → peso 10  | ((100 - avg_umidade) / 100) * 10
#
# Score final = soma dos componentes, limitado a [0.0, 100.0]
# ─────────────────────────────────────────────────────────────


def _classify(score: float) -> str:
    if score <= 24:
        return "Low"
    if score <= 49:
        return "Moderate"
    if score <= 74:
        return "High"
    return "Critical"


def _compute(region_id: int) -> dict:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT AVG(m.temperature), AVG(m.humidity), COUNT(*)
        FROM measurements m
        JOIN sensors s ON s.id = m.sensor_id
        WHERE s.region_id = ?
          AND m.created_at >= datetime('now', '-30 days')
        """,
        (region_id,),
    )
    row = cur.fetchone()
    avg_temp = row[0] or 0.0
    avg_humidity = row[1] or 50.0
    total_count = row[2] or 0

    cur.execute(
        """
        SELECT COUNT(*)
        FROM measurements m
        JOIN sensors s ON s.id = m.sensor_id
        WHERE s.region_id = ?
          AND m.temperature >= 35
          AND m.created_at >= datetime('now', '-30 days')
        """,
        (region_id,),
    )
    high_count = cur.fetchone()[0] or 0

    cur.execute(
        """
        SELECT COUNT(DISTINCT strftime('%Y-%m-%d %H', m.created_at))
        FROM measurements m
        JOIN sensors s ON s.id = m.sensor_id
        WHERE s.region_id = ?
          AND m.temperature >= 35
          AND m.created_at >= datetime('now', '-30 days')
        """,
        (region_id,),
    )
    hot_hours = cur.fetchone()[0] or 0

    cur.execute(
        """
        SELECT COUNT(DISTINCT strftime('%Y-%m-%d %H', m.created_at))
        FROM measurements m
        JOIN sensors s ON s.id = m.sensor_id
        WHERE s.region_id = ?
          AND m.created_at >= datetime('now', '-30 days')
        """,
        (region_id,),
    )
    total_hours = cur.fetchone()[0] or 1

    conn.close()

    high_freq = high_count / total_count if total_count > 0 else 0.0
    critical_duration = hot_hours / total_hours if total_hours > 0 else 0.0
    humidity_penalty = max(0.0, (100.0 - avg_humidity) / 100.0)

    score = (
        (avg_temp / 50.0) * 40.0
        + high_freq * 30.0
        + critical_duration * 20.0
        + humidity_penalty * 10.0
    )
    score = round(min(100.0, max(0.0, score)), 2)

    return {
        "score": score,
        "classification": _classify(score),
        "average_temperature": round(avg_temp, 2),
        "high_temperature_frequency": round(high_freq, 4),
        "critical_duration": round(critical_duration, 4),
    }


def save_heatscore(region_id: int) -> dict:
    data = _compute(region_id)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO heat_scores (
            region_id, score, classification, average_temperature,
            high_temperature_frequency, critical_duration, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            region_id,
            data["score"],
            data["classification"],
            data["average_temperature"],
            data["high_temperature_frequency"],
            data["critical_duration"],
            datetime.now(),
        ),
    )
    conn.commit()
    conn.close()
    return data


def get_heatscore_by_region(region_id: int) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT score, classification, average_temperature,
               high_temperature_frequency, critical_duration, created_at
        FROM heat_scores
        WHERE region_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (region_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "score": row[0],
        "classification": row[1],
        "average_temperature": row[2],
        "high_temperature_frequency": row[3],
        "critical_duration": row[4],
        "created_at": row[5],
    }


def get_heatscore_history(region_id: int) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT score, classification, average_temperature,
               high_temperature_frequency, critical_duration, created_at
        FROM heat_scores
        WHERE region_id = ?
          AND created_at >= datetime('now', '-30 days')
        ORDER BY created_at ASC
        """,
        (region_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "score": r[0],
            "classification": r[1],
            "average_temperature": r[2],
            "high_temperature_frequency": r[3],
            "critical_duration": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]


def get_ranking() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT hs.region_id, r.name, hs.score, hs.classification,
               hs.average_temperature, hs.high_temperature_frequency,
               hs.critical_duration, hs.created_at
        FROM heat_scores hs
        JOIN regions r ON r.id = hs.region_id
        WHERE hs.id IN (
            SELECT MAX(id) FROM heat_scores GROUP BY region_id
        )
        ORDER BY hs.score DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "region_id": r[0],
            "region_name": r[1],
            "score": r[2],
            "classification": r[3],
            "average_temperature": r[4],
            "high_temperature_frequency": r[5],
            "critical_duration": r[6],
            "created_at": r[7],
        }
        for r in rows
    ]
