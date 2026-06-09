import serial
import serial.tools.list_ports

from services.parser_service import parse_serial_line
from services.sensor_service import get_sensor_by_code
from services.measurement_service import save_measurement


def detect_serial_port() -> str:
    ports = list(serial.tools.list_ports.comports())

    for port in ports:
        description = (port.description or "").lower()

        if any(
            keyword in description
            for keyword in ["arduino", "ch340", "cp210", "usb serial", "uart"]
        ):
            return port.device

    if ports:
        return ports[0].device

    raise RuntimeError("No serial port found.")


def start_serial_reader(port: str | None = None, baudrate: int = 9600):

    if port is None:
        port = detect_serial_port()

    connection = serial.Serial(port, baudrate, timeout=2)

    print(f"Connected to {port}")

    while True:
        try:
            raw_line = connection.readline().decode("utf-8", errors="ignore").strip()

            if not raw_line:
                continue

            payload = parse_serial_line(raw_line)

            if payload is None:
                continue

            sensor = get_sensor_by_code(payload["sensor_code"])

            if sensor is None:
                print(f"Sensor not found: {payload['sensor_code']}")

                continue

            save_measurement(
                sensor_id=sensor[0],
                temperature=payload["temperature"],
                humidity=payload["humidity"],
            )

            print(
                f"{payload['sensor_code']} | "
                f"{payload['temperature']}°C | "
                f"{payload['humidity']}%"
            )

        except Exception as error:
            print(f"Serial error: {error}")
