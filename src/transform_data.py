import logging

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

columns_names_to_drop = [
    "weather",
    "weather_icon",
    "sys.type"
]

columns_names_to_rename = {
    "base": "base",
    "visibility": "visibility",
    "dt": "datetime",
    "timezone": "timezone",
    "id": "city_id",
    "name": "city_name",
    "cod": "code",
    "coord.lon": "longitude",
    "coord.lat": "latitude",
    "main.temp": "temperature",
    "main.feels_like": "feels_like",
    "main.temp_min": "temp_min",
    "main.temp_max": "temp_max",
    "main.pressure": "pressure",
    "main.humidity": "humidity",
    "main.sea_level": "sea_level",
    "main.grnd_level": "grnd_level",
    "wind.speed": "wind_speed",
    "wind.deg": "wind_deg",
    "wind.gust": "wind_gust",
    "clouds.all": "clouds",
    "sys.type": "sys_type",
    "sys.id": "sys_id",
    "sys.country": "country",
    "sys.sunrise": "sunrise",
    "sys.sunset": "sunset",
}

columns_to_normalize_datetime = [
    "datetime",
    "sunrise",
    "sunset"
]


def create_dataframe(weather_data: dict) -> pd.DataFrame:
    logging.info("Criando DataFrame a partir do JSON da API...")

    df = pd.json_normalize(weather_data)

    logging.info(
        f"DataFrame criado com sucesso | linhas={len(df)} | colunas={len(df.columns)}"
    )

    return df


def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:

    weather_df = pd.json_normalize(df["weather"].apply(lambda x: x[0]))

    weather_df = weather_df.rename(columns={
        "id": "weather_id",
        "main": "weather_main",
        "description": "weather_description",
        "icon": "weather_icon"
    })

    df = pd.concat([df, weather_df], axis=1)

    logging.info("Colunas de weather normalizadas.")

    return df


def drop_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:

    df = df.drop(columns=columns, errors="ignore")

    logging.info(f"Colunas removidas: {columns}")

    return df


def rename_columns(df: pd.DataFrame, columns: dict[str, str]) -> pd.DataFrame:

    df = df.rename(columns=columns)

    logging.info("Colunas renomeadas.")

    return df


def normalize_datetime_columns(
    df: pd.DataFrame,
    columns: list[str]
) -> pd.DataFrame:

    for column in columns:

        df[column] = (
            pd.to_datetime(df[column], unit="s", utc=True)
            .dt.tz_convert("America/Sao_Paulo")
        )

    logging.info("Datas convertidas para timezone America/Sao_Paulo.")

    return df


def data_transformation(weather_data: dict) -> pd.DataFrame:

    logging.info("Iniciando transformação dos dados...")

    df = create_dataframe(weather_data)

    df = normalize_weather_columns(df)

    df = drop_columns(df, columns_names_to_drop)

    df = rename_columns(df, columns_names_to_rename)

    df = normalize_datetime_columns(df, columns_to_normalize_datetime)

    logging.info("TRANSFORM concluído com sucesso.")

    return df