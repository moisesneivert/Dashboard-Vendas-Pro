from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class SalesKPIs:
    revenue: float
    profit: float
    orders: int
    items: int
    average_ticket: float
    margin_pct: float


def calculate_kpis(frame: pd.DataFrame) -> SalesKPIs:
    if frame.empty:
        return SalesKPIs(0.0, 0.0, 0, 0, 0.0, 0.0)
    revenue = float(frame["revenue"].sum())
    profit = float(frame["profit"].sum())
    orders = int(frame["order_id"].nunique())
    items = int(frame["quantity"].sum())
    return SalesKPIs(
        revenue=revenue,
        profit=profit,
        orders=orders,
        items=items,
        average_ticket=revenue / orders if orders else 0.0,
        margin_pct=profit / revenue * 100 if revenue else 0.0,
    )


def monthly_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["month", "revenue", "profit", "orders", "items"])
    return (
        frame.groupby("month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
            items=("quantity", "sum"),
        )
        .sort_values("month")
        .reset_index(drop=True)
    )


def percentage_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current - previous) / abs(previous) * 100


def latest_month_changes(frame: pd.DataFrame) -> dict[str, float | None]:
    monthly = monthly_summary(frame)
    if len(monthly) < 2:
        return {"revenue": None, "profit": None, "orders": None}
    current, previous = monthly.iloc[-1], monthly.iloc[-2]
    return {
        "revenue": percentage_change(float(current["revenue"]), float(previous["revenue"])),
        "profit": percentage_change(float(current["profit"]), float(previous["profit"])),
        "orders": percentage_change(float(current["orders"]), float(previous["orders"])),
    }
