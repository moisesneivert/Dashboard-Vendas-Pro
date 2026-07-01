import pandas as pd
import pytest

from src.dashboard.data_processing import prepare_sales_data
from src.dashboard.exceptions import DataValidationError


def test_prepare_sales_data_calculates_business_columns(raw_sales):
    sales, report = prepare_sales_data(raw_sales)
    assert sales.loc[0, "revenue"] == 4000
    assert sales.loc[0, "profit"] == 1000
    assert report.valid_rows == 6


def test_prepare_sales_data_accepts_portuguese_aliases(raw_sales):
    aliases = raw_sales.rename(
        columns={
            "sale_date": "data",
            "order_id": "pedido",
            "region": "regiao",
            "state": "estado",
            "category": "categoria",
            "product": "produto",
            "seller": "vendedor",
            "channel": "canal",
            "payment_status": "status_pagamento",
            "quantity": "quantidade",
            "unit_price": "preco_unitario",
            "unit_cost": "custo_unitario",
        }
    )
    sales, _ = prepare_sales_data(aliases)
    assert "revenue" in sales.columns


def test_prepare_sales_data_removes_invalid_rows(raw_sales):
    raw_sales.loc[0, "quantity"] = -1
    sales, report = prepare_sales_data(raw_sales)
    assert len(sales) == 5
    assert report.removed_rows == 1


def test_prepare_sales_data_rejects_missing_columns(raw_sales):
    with pytest.raises(DataValidationError):
        prepare_sales_data(raw_sales.drop(columns="seller"))


def test_prepare_sales_data_rejects_empty_frame():
    with pytest.raises(DataValidationError):
        prepare_sales_data(pd.DataFrame())
