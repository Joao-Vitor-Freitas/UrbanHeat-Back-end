import time
import random
import requests

API_URL = "http://127.0.0.1:8000/measurements/"
SENSOR_CODE = "A1"


def simulate_measurements():
    print(f"Iniciando simulação do sensor {SENSOR_CODE}...")

    while True:
        temp = round(random.uniform(25.0, 38.0), 2)
        hum = round(random.uniform(40.0, 70.0), 2)

        payload = {"sensor_code": SENSOR_CODE, "temperature": temp, "humidity": hum}

        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 201:
                print(
                    f"Enviado: Temp {temp}°C | Umi {hum}% -> Status: {response.status_code}"
                )
            else:
                print(f"Erro da API: {response.text}")
        except requests.exceptions.ConnectionError:
            print("Erro: API não está rodando em http://127.0.0.1:8000")

        time.sleep(2)


if __name__ == "__main__":
    simulate_measurements()
