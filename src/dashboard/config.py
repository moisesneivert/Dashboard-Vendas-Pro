from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SALES_FILE = BASE_DIR / "data" / "vendas_exemplo.csv"
DEFAULT_GOALS_FILE = BASE_DIR / "data" / "metas_vendas.csv"


@dataclass(frozen=True, slots=True)
class AppSettings:
    app_name: str = "Dashboard de Vendas Pro"
    sales_file: Path = DEFAULT_SALES_FILE
    goals_file: Path = DEFAULT_GOALS_FILE
    database_url: str | None = None
    database_query: str = "SELECT * FROM sales ORDER BY sale_date"

    @classmethod
    def from_environment(cls) -> AppSettings:
        load_dotenv(BASE_DIR / ".env")
        return cls(
            database_url=os.getenv("DATABASE_URL"),
            database_query=os.getenv("DATABASE_QUERY", "SELECT * FROM sales ORDER BY sale_date"),
        )
