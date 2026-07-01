from __future__ import annotations

import pandas as pd

from .metrics import monthly_summary


def _leader(frame: pd.DataFrame, column: str, metric: str = "revenue") -> tuple[str, float] | None:
    if frame.empty:
        return None
    grouped = frame.groupby(column, dropna=False)[metric].sum().sort_values(ascending=False)
    if grouped.empty:
        return None
    return str(grouped.index[0]), float(grouped.iloc[0])


def generate_insights(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["Nenhum dado disponível para gerar insights."]

    insights: list[str] = []
    for label, column in (
        ("categoria", "category"),
        ("produto", "product"),
        ("vendedor", "seller"),
        ("canal", "channel"),
    ):
        result = _leader(frame, column)
        if result:
            name, value = result
            insights.append(f"Melhor {label}: **{name}**, com faturamento de R$ {value:,.2f}.")

    monthly = monthly_summary(frame)
    if len(monthly) >= 2:
        current, previous = monthly.iloc[-1], monthly.iloc[-2]
        if previous["revenue"]:
            change = (current["revenue"] - previous["revenue"]) / abs(previous["revenue"]) * 100
            direction = "cresceu" if change >= 0 else "caiu"
            insights.append(
                f"O faturamento do último mês {direction} **{abs(change):.1f}%** em relação ao anterior."
            )

    margins = frame.groupby("category")["margin_pct"].mean().sort_values()
    if not margins.empty:
        insights.append(
            f"Categoria com menor margem média: **{margins.index[0]}** ({margins.iloc[0]:.1f}%)."
        )
    return insights
