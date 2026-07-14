import logging
import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

from extract_data import extract_weather_data
from transform_data import data_transformation
from load_data import load_weather_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(env_path)


API_KEY = os.getenv("API_KEY")

CITIES = [
    "Sao Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Porto Alegre",
    "Salvador",
    "Fortaleza",
    "Recife",
    "Brasilia",
    "Goiania",
    "Manaus",
    "Belem",
    "Natal",
    "Joao Pessoa",
    "Maceio",
    "Aracaju",
    "Campo Grande",
    "Cuiaba",
    "Palmas",
    "Florianopolis"
]


def main():

    all_dataframes = []
    
    for city in CITIES:

        logging.info(f"Processando cidade: {city}")

        weather_data = extract_weather_data(city, API_KEY)

        if not weather_data:
            continue

        try:
            df = data_transformation(weather_data)
            all_dataframes.append(df)
        except Exception as e:
            logging.error(f"Erro ao processar {city}: {e}")
            continue

    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        load_weather_data("weather_data", final_df)
    else:
        logging.warning("Nenhuma cidade foi processada com sucesso.")

    logging.info("Pipeline finalizada com sucesso!")


if __name__ == "__main__":
    main()