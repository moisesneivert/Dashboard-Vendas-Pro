from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def revenue_profit_over_time(monthly: pd.DataFrame) -> go.Figure:
    melted = monthly.melt(
        id_vars="month", value_vars=["revenue", "profit"], var_name="metric", value_name="value"
    )
    labels = {"revenue": "Faturamento", "profit": "Lucro"}
    melted["metric"] = melted["metric"].map(labels)
    fig = px.line(melted, x="month", y="value", color="metric", markers=True)
    fig.update_layout(xaxis_title="Mês", yaxis_title="Valor (R$)", legend_title="Indicador")
    return fig


def ranking_bar(frame: pd.DataFrame, dimension: str, title: str, top_n: int = 10) -> go.Figure:
    ranking = (
        frame.groupby(dimension, as_index=False)["revenue"]
        .sum()
        .nlargest(top_n, "revenue")
        .sort_values("revenue")
    )
    fig = px.bar(ranking, x="revenue", y=dimension, orientation="h", title=title)
    fig.update_layout(xaxis_title="Faturamento (R$)", yaxis_title=None)
    return fig


def channel_share(frame: pd.DataFrame) -> go.Figure:
    data = frame.groupby("channel", as_index=False)["revenue"].sum()
    return px.pie(
        data, names="channel", values="revenue", hole=0.45, title="Participação por canal"
    )


def margin_by_category(frame: pd.DataFrame) -> go.Figure:
    data = frame.groupby("category", as_index=False).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum")
    )
    data["margin_pct"] = data["profit"].div(data["revenue"]).mul(100)
    return px.bar(
        data.sort_values("margin_pct"), x="category", y="margin_pct", title="Margem por categoria"
    )


def goal_chart(performance: pd.DataFrame, actual: str, goal: str, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=performance["month"], y=performance[actual], name="Realizado"))
    fig.add_trace(
        go.Scatter(x=performance["month"], y=performance[goal], name="Meta", mode="lines+markers")
    )
    fig.update_layout(title=title, xaxis_title="Mês", yaxis_title="Valor (R$)", barmode="group")
    return fig


def forecast_chart(forecast: pd.DataFrame) -> go.Figure:
    return px.line(
        forecast,
        x="month",
        y="revenue",
        color="series",
        markers=True,
        title="Faturamento realizado e previsão",
        labels={"month": "Mês", "revenue": "Faturamento (R$)", "series": "Série"},
    )
