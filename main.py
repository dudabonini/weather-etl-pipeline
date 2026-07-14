"""Entry point para rodar o pipeline ETL localmente, fora do Airflow.

Uso:
    python main.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from main import main  # noqa: E402  (src/main.py)

if __name__ == "__main__":
    main()
