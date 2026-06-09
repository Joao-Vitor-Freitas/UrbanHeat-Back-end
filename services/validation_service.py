MIN_TEMPERATURE = -10.0
MAX_TEMPERATURE = 60.0

MIN_HUMIDITY = 0.0
MAX_HUMIDITY = 100.0


def validate_measurement(temperature: float, humidity: float) -> tuple[bool, str]:

    if not (MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE):
        return (
            False,
            f"Temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}",
        )

    if not (MIN_HUMIDITY <= humidity <= MAX_HUMIDITY):
        return (False, f"Humidity must be between {MIN_HUMIDITY} and {MAX_HUMIDITY}")

    return True, ""
