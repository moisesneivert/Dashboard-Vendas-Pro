from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True, slots=True)
class SalesFilters:
    start_date: date | None = None
    end_date: date | None = None
    regions: tuple[str, ...] = ()
    states: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    products: tuple[str, ...] = ()
    sellers: tuple[str, ...] = ()
    channels: tuple[str, ...] = ()
    payment_statuses: tuple[str, ...] = ()


def _filter_values(frame: pd.DataFrame, column: str, values: tuple[str, ...]) -> pd.DataFrame:
    return frame.loc[frame[column].isin(values)] if values else frame


def apply_filters(frame: pd.DataFrame, filters: SalesFilters) -> pd.DataFrame:
    result = frame.copy()
    if filters.start_date:
        result = result.loc[result["sale_date"].dt.date >= filters.start_date]
    if filters.end_date:
        result = result.loc[result["sale_date"].dt.date <= filters.end_date]

    mapping = {
        "region": filters.regions,
        "state": filters.states,
        "category": filters.categories,
        "product": filters.products,
        "seller": filters.sellers,
        "channel": filters.channels,
        "payment_status": filters.payment_statuses,
    }
    for column, values in mapping.items():
        result = _filter_values(result, column, values)
    return result.reset_index(drop=True)
