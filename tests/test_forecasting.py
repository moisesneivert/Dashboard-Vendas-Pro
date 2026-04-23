import pandas as pd

from src.forecasting import forecast_monthly_sales


def test_forecast_monthly_sales_returns_requested_months():
    df = pd.DataFrame(
        {
            "mes": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-03-01"]),
            "faturamento": [1000, 1200, 1400],
        }
    )

    forecast = forecast_monthly_sales(df, months_ahead=2)

    assert len(forecast) == 2
    assert "faturamento_previsto" in forecast.columns