import pandas as pd

from src.data_processing import prepare_sales_data
from src.goals import analyze_goals


def test_analyze_goals_marks_goal_as_achieved():
    df = pd.DataFrame(
        [
            {
                "data": "2026-01-10",
                "pedido_id": "PED-1",
                "cliente": "Cliente A",
                "cidade": "Natal",
                "estado": "RN",
                "regiao": "Nordeste",
                "produto": "Produto A",
                "categoria": "Categoria A",
                "vendedor": "Ana",
                "canal_venda": "E-commerce",
                "quantidade": 2,
                "preco_unitario": 100,
                "custo_unitario": 60,
                "status_pagamento": "Pago",
            }
        ]
    )

    sales, _ = prepare_sales_data(df)

    goals = pd.DataFrame(
        [
            {
                "mes": pd.Timestamp("2026-01-01"),
                "meta_faturamento": 100,
                "meta_lucro": 50,
            }
        ]
    )

    result = analyze_goals(sales, goals)

    assert result.loc[0, "status_meta"] == "Atingida"
    assert result.loc[0, "atingimento_faturamento_%"] == 200