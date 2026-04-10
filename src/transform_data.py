import pandas as pd
from pathlib import Path
import json
import logging 



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

path_name = Path(__file__).parent.parent / 'data' / 'weather_data.json'
columns_names_to_drop = ['weather', 'weather_icon', 'sys.type']
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
        # weather_id, weather_main, weather_description 
    }
columns_to_normalize_datetime = ['datetime', 'sunrise', 'sunset']

def create_dataframe(path_name:str) -> pd.DataFrame:
    logging.info(f"Criando dataframe do arquivo JSON: {path_name}")
    path = path_name

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    
    with open(path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    logging.info(f"Dataframe criado com sucesso. Número de linhas: {len(df)}, Número de colunas: {len(df.columns)}")
    return df

def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))

    df_weather = df_weather.rename(columns={
        'id': 'weather_id',
        'main': 'weather_main',
        'description': 'weather_description',
        'icon': 'weather_icon'
    })

    df = pd.concat([df,df_weather], axis=1)
    logging.info("Colunas de weather normalizadas e concatenadas ao dataframe principal.")
    return df


def drop_columns(df: pd.DataFrame, columns_names: list[str]) -> pd.DataFrame:
    logging.info(f"Removendo colunas: {columns_names}")
    df = df.drop(columns=columns_names)
    logging.info(f"Colunas removidas com sucesso. Colunas restantes: {df.columns.tolist()}")
    return df


def rename_columns(df: pd.DataFrame, columns_names: dict[str, str]) -> pd.DataFrame:
    logging.info(f"Renomeando colunas: {columns_names}")
    df = df.rename(columns=columns_names)
    logging.info(f'Colunas renomeadas com sucesso')
    return df


def normalize_datetime_columns(df:pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:
    logging.info(f"Normalizando colunas de datetime: {columns_names}")
    for name in columns_names:
        logging.info(f"Normalizando coluna: {name}")
        df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert('America/Sao_Paulo')
    logging.info(f"Colunas de datetime normalizadas: {columns_names}")
    return df

def data_transformation():
   print("Iniciando processo de transformação dos dados...")
   df = create_dataframe(path_name)
   df = normalize_weather_columns(df)
   df = drop_columns(df, columns_names_to_drop)    
   df = rename_columns(df, columns_names_to_rename)
   df = normalize_datetime_columns(df, columns_to_normalize_datetime)
   logging.info("Processo de transformação dos dados concluído com sucesso.")
   return df