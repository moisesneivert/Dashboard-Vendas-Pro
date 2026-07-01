from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main() -> None:
    from src.dashboard.config import DEFAULT_SALES_FILE
    from src.dashboard.data_processing import prepare_sales_data
    from src.dashboard.data_sources import load_csv

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("Defina DATABASE_URL antes de executar este script.")
    sales, _ = prepare_sales_data(load_csv(DEFAULT_SALES_FILE))
    database_frame = sales[
        [
            "sale_date",
            "order_id",
            "region",
            "state",
            "category",
            "product",
            "seller",
            "channel",
            "payment_status",
            "quantity",
            "unit_price",
            "unit_cost",
        ]
    ]
    engine = create_engine(database_url)
    try:
        database_frame.to_sql("sales", engine, if_exists="replace", index=False)
    finally:
        engine.dispose()
    print(f"{len(database_frame)} registros inseridos na tabela sales.")


if __name__ == "__main__":
    main()
