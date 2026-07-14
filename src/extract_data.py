import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_weather_data(city: str, api_key: str) -> dict:
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city},BR&units=metric&appid={api_key}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição para {city}: {e}")
        return {}

    data = response.json()

    logging.info(f"EXTRACT concluído | city={city}")

    return data