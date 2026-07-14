import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task
from dotenv import load_dotenv

sys.path.insert(0, '/opt/airflow/src')

from extract_data import extract_weather_data
from load_data import load_weather_data
from transform_data import data_transformation

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('API_KEY')

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
    "Florianopolis",
]

TABLE_NAME = "weather_data"
PARQUET_PATH = "/opt/airflow/data/temp_data.parquet"


@dag(
    dag_id='weather_pipeline',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    description='Pipeline ETL - Clima de 20 capitais brasileiras',
    schedule='0 * * * *',
    start_date=datetime(2026, 2, 7),
    catchup=False,
    tags=['weather', 'etl'],
)
def weather_pipeline():

    @task
    def extract() -> list[dict]:
        raw_data = []
        for city in CITIES:
            data = extract_weather_data(city, API_KEY)
            if data:
                raw_data.append(data)
            else:
                logging.warning(f"Sem dados para {city}, pulando.")
        return raw_data

    @task
    def transform(raw_data: list[dict]) -> str:
        import pandas as pd

        dataframes = []
        for weather_data in raw_data:
            try:
                dataframes.append(data_transformation(weather_data))
            except Exception as e:
                logging.error(f"Erro ao transformar dados: {e}")

        if not dataframes:
            raise ValueError("Nenhum dado foi transformado com sucesso.")

        df = pd.concat(dataframes, ignore_index=True)
        df.to_parquet(PARQUET_PATH, index=False)
        return PARQUET_PATH

    @task
    def load(parquet_path: str):
        import pandas as pd

        df = pd.read_parquet(parquet_path)
        load_weather_data(TABLE_NAME, df)

    load(transform(extract()))


weather_pipeline()
