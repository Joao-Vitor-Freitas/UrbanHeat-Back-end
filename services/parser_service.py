import json


def parse_serial_line(line: str):

    line = line.strip()

    if not line:
        return None

    if line.startswith("{"):
        try:
            payload = json.loads(line)

            return {
                "sensor_code": payload["sensor_id"],
                "temperature": float(payload["temperature"]),
                "humidity": float(payload["humidity"]),
            }

        except Exception:
            return None

    parts = line.split(",")

    if len(parts) != 3:
        return None

    try:
        return {
            "sensor_code": parts[0].strip(),
            "temperature": float(parts[1]),
            "humidity": float(parts[2]),
        }

    except Exception:
        return None
