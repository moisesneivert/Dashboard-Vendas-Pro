from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

from .exceptions import ForecastError
from .metrics import monthly_summary


def forecast_monthly_revenue(
    frame: pd.DataFrame, periods: int = 3
) -> tuple[pd.DataFrame, dict[str, float]]:
    if periods < 1 or periods > 12:
        raise ForecastError("O horizonte de previsão deve estar entre 1 e 12 meses.")

    monthly = monthly_summary(frame)[["month", "revenue"]].copy()
    if len(monthly) < 6:
        raise ForecastError("São necessários pelo menos 6 meses de dados para gerar a previsão.")

    x = np.arange(len(monthly), dtype=float).reshape(-1, 1)
    y = monthly["revenue"].to_numpy(dtype=float)
    model = LinearRegression().fit(x, y)
    fitted = model.predict(x)

    future_x = np.arange(len(monthly), len(monthly) + periods, dtype=float).reshape(-1, 1)
    future_dates = pd.date_range(
        monthly["month"].max() + pd.offsets.MonthBegin(1), periods=periods, freq="MS"
    )
    future = pd.DataFrame(
        {
            "month": future_dates,
            "revenue": np.maximum(model.predict(future_x), 0.0),
            "series": "Previsão",
        }
    )
    history = monthly.assign(series="Realizado")
    combined = pd.concat([history, future], ignore_index=True)
    metrics = {
        "mae": float(mean_absolute_error(y, fitted)),
        "r2": float(r2_score(y, fitted)),
        "monthly_trend": float(model.coef_[0]),
    }
    return combined, metrics
