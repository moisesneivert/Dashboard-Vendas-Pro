import pandas as pd

from src.data_processing import prepare_sales_data


def test_prepare_sales_data_calculates_metrics():
    df = pd.DataFrame(
        [
            {
                "data": "2026-01-01",
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

    prepared, invalid_states = prepare_sales_data(df)

    assert invalid_states == []
    assert prepared.loc[0, "faturamento"] == 200
    assert prepared.loc[0, "lucro"] == 80
    assert prepared.loc[0, "margem_percentual"] == 40


def test_prepare_sales_data_removes_invalid_states():
    df = pd.DataFrame(
        [
            {
                "data": "2026-01-01",
                "pedido_id": "PED-1",
                "cliente": "Cliente A",
                "cidade": "Natal",
                "estado": "Enfermeira",
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

    prepared, invalid_states = prepare_sales_data(df)

    assert "ENFERMEIRA" in invalid_states
    assert prepared.empty