import logging
import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# Carrega variáveis de ambiente
# ==============================

env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(env_path)

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DB_NAME")
HOST = os.getenv("DB_HOST", "localhost")
PORT = os.getenv("DB_PORT", "5432")

# ==============================
# Conexão com PostgreSQL
# ==============================

def get_engine() -> Engine:
    logging.info(f"Conectando ao banco {DATABASE} em {HOST}:{PORT}")

    return create_engine(
        f"postgresql+psycopg2://{USER}:{quote_plus(PASSWORD)}@{HOST}:{PORT}/{DATABASE}"
    )


# ==============================
# LOAD
# ==============================

def load_weather_data(
    table_name: str,
    df: pd.DataFrame
) -> None:
    """Carrega os dados de forma idempotente: rodar a mesma leitura duas
    vezes (ex: dois disparos manuais próximos, quando a API ainda não
    atualizou) não duplica linhas. A unicidade é garantida por
    (city_name, datetime) via uma constraint UNIQUE + INSERT ... ON
    CONFLICT DO NOTHING."""

    logging.info(f"Iniciando LOAD da tabela '{table_name}'")

    engine = get_engine()
    staging_table = f"_staging_{table_name}"
    constraint_name = f"{table_name}_city_datetime_key"
    columns = ", ".join(f'"{c}"' for c in df.columns)

    try:
        with engine.begin() as conn:
            # 1. escreve o lote novo numa tabela temporária de staging
            df.to_sql(name=staging_table, con=conn, if_exists="replace", index=False)

            # 2. garante que a tabela final existe, com a mesma estrutura
            conn.execute(text(
                f'CREATE TABLE IF NOT EXISTS "{table_name}" '
                f'(LIKE "{staging_table}" INCLUDING ALL)'
            ))

            # 2.1 evolução de esquema: a API só manda campos como "rain.1h"
            # (chuva na última hora) quando está chovendo naquela cidade, ou
            # "snow.1h" quando neva. Isso faz colunas novas aparecerem em
            # lotes futuros que a tabela ainda não tem — adiciona
            # automaticamente em vez de quebrar o load.
            staging_cols = conn.execute(text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = :t"
            ), {"t": staging_table}).all()
            existing_cols = {
                row[0] for row in conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = :t"
                ), {"t": table_name}).all()
            }
            for col_name, data_type in staging_cols:
                if col_name not in existing_cols:
                    logging.info(f"Coluna nova detectada, adicionando: {col_name} ({data_type})")
                    conn.execute(text(
                        f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS '
                        f'"{col_name}" {data_type}'
                    ))

            # 3. garante a constraint de unicidade (só cria se ainda não existir)
            conn.execute(text(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint WHERE conname = '{constraint_name}'
                    ) THEN
                        ALTER TABLE "{table_name}"
                        ADD CONSTRAINT {constraint_name} UNIQUE (city_name, datetime);
                    END IF;
                END $$;
            """))

            # 4. insere só o que ainda não existe (idempotente)
            result = conn.execute(text(
                f'INSERT INTO "{table_name}" ({columns}) '
                f'SELECT {columns} FROM "{staging_table}" '
                f'ON CONFLICT (city_name, datetime) DO NOTHING'
            ))
            inseridos = result.rowcount

            conn.execute(text(f'DROP TABLE IF EXISTS "{staging_table}"'))

        with engine.connect() as conn:
            total = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()

        logging.info(
            f"LOAD concluído | tabela={table_name} | "
            f"novos registros={inseridos} | duplicados ignorados={len(df) - inseridos} | "
            f"total na tabela={total}"
        )

    except Exception as e:
        logging.error(f"Erro durante o LOAD: {e}")
        raise