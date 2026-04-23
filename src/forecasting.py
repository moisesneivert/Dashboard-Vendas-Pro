import pandas as pd
from sklearn.linear_model import LinearRegression


def forecast_monthly_sales(sales_df: pd.DataFrame, months_ahead: int = 3) -> pd.DataFrame:
    monthly = (
        sales_df.groupby("mes", as_index=False)
        .agg(faturamento=("faturamento", "sum"))
        .sort_values("mes")
    )

    if len(monthly) < 3:
        raise ValueError("É necessário ter pelo menos 3 meses de dados para gerar previsão.")

    monthly["indice_mes"] = range(len(monthly))

    model = LinearRegression()
    model.fit(monthly[["indice_mes"]], monthly["faturamento"])

    future_indexes = list(range(len(monthly), len(monthly) + months_ahead))
    last_month = monthly["mes"].max()

    future_months = pd.date_range(
        start=last_month + pd.offsets.MonthBegin(1),
        periods=months_ahead,
        freq="MS",
    )

    predictions = model.predict(pd.DataFrame({"indice_mes": future_indexes}))
    predictions = [max(0, round(float(value), 2)) for value in predictions]

    forecast_df = pd.DataFrame(
        {
            "mes": future_months,
            "faturamento_previsto": predictions,
        }
    )

    return forecast_df