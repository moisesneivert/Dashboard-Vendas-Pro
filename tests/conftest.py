from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def raw_sales() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sale_date": [
                "2026-01-10",
                "2026-02-12",
                "2026-03-15",
                "2026-04-20",
                "2026-05-10",
                "2026-06-01",
            ],
            "order_id": ["A1", "A2", "A3", "A4", "A5", "A6"],
            "region": ["Sul"] * 6,
            "state": ["PR"] * 6,
            "category": ["Hardware", "Hardware", "Serviços", "Serviços", "Hardware", "Serviços"],
            "product": ["Notebook", "Monitor", "Suporte", "Instalação", "Teclado", "Consultoria"],
            "seller": ["Ana", "Bruno", "Ana", "Bruno", "Ana", "Bruno"],
            "channel": ["Online", "Loja", "Online", "Loja", "Online", "Loja"],
            "payment_status": ["Pago"] * 6,
            "quantity": [1, 2, 3, 1, 5, 2],
            "unit_price": [4000, 900, 300, 500, 150, 1000],
            "unit_cost": [3000, 600, 100, 200, 80, 400],
        }
    )
