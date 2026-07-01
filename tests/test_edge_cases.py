from __future__ import annotations

from datetime import date

import pandas as pd
import pytest
from sqlalchemy import create_engine

from src.dashboard.auth import authenticate, hash_password, verify_password
from src.dashboard.config import AppSettings
from src.dashboard.data_processing import prepare_sales_data
from src.dashboard.data_sources import load_csv, load_sales_from_database
from src.dashboard.exceptions import DataSourceError, DataValidationError, ForecastError
from src.dashboard.filters import SalesFilters, apply_filters
from src.dashboard.forecasting import forecast_monthly_revenue
from src.dashboard.formatting import delta_percentage, integer_br
from src.dashboard.goals import prepare_goals
from src.dashboard.insights import generate_insights
from src.dashboard.metrics import calculate_kpis, latest_month_changes, monthly_summary


def test_settings_read_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("DATABASE_QUERY", "SELECT 1")
    settings = AppSettings.from_environment()
    assert settings.database_url == "sqlite:///test.db"
    assert settings.database_query == "SELECT 1"


def test_verify_password_rejects_invalid_encodings():
    assert not verify_password("Senha@123", "argon2$1$abc$def")
    assert not verify_password("Senha@123", "malformed")


def test_authenticate_uses_default_profile_fields():
    encoded = hash_password("Senha@123")
    user = authenticate("viewer", "Senha@123", [{"username": "viewer", "password_hash": encoded}])
    assert user is not None
    assert user.name == "viewer"
    assert user.role == "viewer"


def test_load_csv_wraps_read_errors(tmp_path):
    with pytest.raises(DataSourceError):
        load_csv(tmp_path / "missing.csv")


def test_database_requires_url():
    with pytest.raises(DataSourceError):
        load_sales_from_database("", "SELECT 1")


def test_database_loads_select_query(tmp_path):
    database = tmp_path / "sales.db"
    url = f"sqlite:///{database}"
    engine = create_engine(url)
    try:
        pd.DataFrame({"value": [1, 2]}).to_sql("items", engine, index=False)
    finally:
        engine.dispose()
    frame = load_sales_from_database(url, "SELECT * FROM items ORDER BY value")
    assert frame["value"].tolist() == [1, 2]


def test_database_wraps_sqlalchemy_error(tmp_path):
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    with pytest.raises(DataSourceError):
        load_sales_from_database(url, "SELECT * FROM missing_table")


def test_filters_apply_end_date_and_values(raw_sales):
    sales, _ = prepare_sales_data(raw_sales)
    result = apply_filters(
        sales,
        SalesFilters(
            end_date=date(2026, 4, 30),
            sellers=("Ana",),
            channels=("Online",),
            payment_statuses=("Pago",),
            states=("PR",),
            regions=("Sul",),
            products=("Notebook", "Suporte"),
        ),
    )
    assert not result.empty
    assert result["sale_date"].max().date() <= date(2026, 4, 30)


def test_forecast_rejects_invalid_period(raw_sales):
    sales, _ = prepare_sales_data(raw_sales)
    with pytest.raises(ForecastError):
        forecast_monthly_revenue(sales, periods=0)


def test_formatting_helpers():
    assert integer_br(12345) == "12.345"
    assert delta_percentage(None) is None
    assert delta_percentage(2.5) == "2,5%"


def test_prepare_goals_rejects_empty_and_missing_columns():
    with pytest.raises(DataValidationError):
        prepare_goals(pd.DataFrame())
    with pytest.raises(DataValidationError):
        prepare_goals(pd.DataFrame({"month": ["2026-01-01"]}))


def test_prepare_goals_supports_aliases_and_drops_invalid():
    goals = prepare_goals(
        pd.DataFrame(
            {
                "mês": ["2026-01-01", "invalid"],
                "meta_faturamento": [1000, "bad"],
                "meta_lucro": [200, "bad"],
            }
        )
    )
    assert len(goals) == 1
    assert goals.iloc[0]["revenue_goal"] == 1000


def test_metrics_empty_and_single_month(raw_sales):
    empty = pd.DataFrame()
    assert calculate_kpis(empty).orders == 0
    assert monthly_summary(empty).empty

    sales, _ = prepare_sales_data(raw_sales.iloc[:1])
    assert latest_month_changes(sales) == {"revenue": None, "profit": None, "orders": None}


def test_insights_empty_and_declining_month(raw_sales):
    assert generate_insights(pd.DataFrame()) == ["Nenhum dado disponível para gerar insights."]
    sales, _ = prepare_sales_data(raw_sales.copy())
    sales.loc[sales["month"] == sales["month"].max(), "revenue"] = 1
    insights = generate_insights(sales)
    assert any("caiu" in item for item in insights)
