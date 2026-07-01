from datetime import date

from src.dashboard.data_processing import prepare_sales_data
from src.dashboard.filters import SalesFilters, apply_filters
from src.dashboard.metrics import (
    calculate_kpis,
    latest_month_changes,
    monthly_summary,
    percentage_change,
)


def test_apply_filters(raw_sales):
    sales, _ = prepare_sales_data(raw_sales)
    filtered = apply_filters(
        sales, SalesFilters(start_date=date(2026, 2, 1), categories=("Hardware",))
    )
    assert filtered["category"].eq("Hardware").all()
    assert filtered["sale_date"].min().date() >= date(2026, 2, 1)


def test_calculate_kpis(raw_sales):
    sales, _ = prepare_sales_data(raw_sales)
    kpis = calculate_kpis(sales)
    assert kpis.orders == 6
    assert kpis.revenue > kpis.profit > 0


def test_monthly_summary_and_changes(raw_sales):
    sales, _ = prepare_sales_data(raw_sales)
    monthly = monthly_summary(sales)
    changes = latest_month_changes(sales)
    assert len(monthly) == 6
    assert changes["revenue"] is not None


def test_percentage_change_handles_zero():
    assert percentage_change(10, 0) is None
