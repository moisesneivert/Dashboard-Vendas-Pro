import pandas as pd
import pytest

from src.dashboard.data_processing import prepare_sales_data
from src.dashboard.exceptions import ForecastError
from src.dashboard.forecasting import forecast_monthly_revenue
from src.dashboard.goals import calculate_goal_performance, prepare_goals
from src.dashboard.insights import generate_insights
from src.dashboard.metrics import monthly_summary


def test_forecast_returns_future_periods(raw_sales):
    sales, _ = prepare_sales_data(raw_sales)
    forecast, metrics = forecast_monthly_revenue(sales, periods=2)
    assert len(forecast) == 8
    assert (forecast["series"] == "Previsão").sum() == 2
    assert "mae" in metrics


def test_forecast_rejects_short_history(raw_sales):
    sales, _ = prepare_sales_data(raw_sales.iloc[:3])
    with pytest.raises(ForecastError):
        forecast_monthly_revenue(sales)


def test_prepare_goals_and_performance(raw_sales):
    sales, _ = prepare_sales_data(raw_sales)
    goals = prepare_goals(
        pd.DataFrame(
            {
                "month": pd.date_range("2026-01-01", periods=6, freq="MS"),
                "revenue_goal": [1000] * 6,
                "profit_goal": [200] * 6,
            }
        )
    )
    result = calculate_goal_performance(monthly_summary(sales), goals)
    assert "revenue_achievement_pct" in result.columns


def test_generate_insights(raw_sales):
    sales, _ = prepare_sales_data(raw_sales)
    insights = generate_insights(sales)
    assert len(insights) >= 5
