from __future__ import annotations

import pandas as pd

from .exceptions import DataValidationError
from .schema import GOAL_ALIASES, GOAL_COLUMNS


def prepare_goals(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        raise DataValidationError("A base de metas está vazia.")
    goals = frame.copy()
    goals.columns = [
        GOAL_ALIASES.get(str(c).strip().lower(), str(c).strip().lower()) for c in goals.columns
    ]
    missing = GOAL_COLUMNS.difference(goals.columns)
    if missing:
        raise DataValidationError("Colunas de metas ausentes: " + ", ".join(sorted(missing)))
    goals["month"] = (
        pd.to_datetime(goals["month"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    )
    goals["revenue_goal"] = pd.to_numeric(goals["revenue_goal"], errors="coerce")
    goals["profit_goal"] = pd.to_numeric(goals["profit_goal"], errors="coerce")
    goals = goals.dropna(subset=["month", "revenue_goal", "profit_goal"])
    return goals.sort_values("month").drop_duplicates("month", keep="last").reset_index(drop=True)


def calculate_goal_performance(monthly: pd.DataFrame, goals: pd.DataFrame) -> pd.DataFrame:
    result = monthly.merge(goals, on="month", how="left")
    result["revenue_achievement_pct"] = result["revenue"].div(result["revenue_goal"]).mul(100)
    result["profit_achievement_pct"] = result["profit"].div(result["profit_goal"]).mul(100)
    result["revenue_gap"] = result["revenue"] - result["revenue_goal"]
    result["profit_gap"] = result["profit"] - result["profit_goal"]
    return result
