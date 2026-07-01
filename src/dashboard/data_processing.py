from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .exceptions import DataValidationError
from .schema import COLUMN_ALIASES, SALES_COLUMNS


@dataclass(frozen=True, slots=True)
class DataQualityReport:
    original_rows: int
    valid_rows: int
    removed_rows: int
    duplicate_orders: int
    missing_values: int
    warnings: tuple[str, ...]


def _slugify_column(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return COLUMN_ALIASES.get(text, text)


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [_slugify_column(column) for column in normalized.columns]
    return normalized


def _missing_columns(columns: Iterable[str]) -> set[str]:
    return SALES_COLUMNS.difference(columns)


def prepare_sales_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, DataQualityReport]:
    if frame is None or frame.empty:
        raise DataValidationError("A base de vendas está vazia.")

    sales = normalize_columns(frame)
    missing = _missing_columns(sales.columns)
    if missing:
        raise DataValidationError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))

    original_rows = len(sales)
    warnings: list[str] = []

    sales["sale_date"] = pd.to_datetime(sales["sale_date"], errors="coerce")
    for column in ("quantity", "unit_price", "unit_cost"):
        sales[column] = pd.to_numeric(sales[column], errors="coerce")

    text_columns = [
        "order_id",
        "region",
        "state",
        "category",
        "product",
        "seller",
        "channel",
        "payment_status",
    ]
    for column in text_columns:
        sales[column] = sales[column].astype("string").str.strip()

    required_for_row = [
        "sale_date",
        "order_id",
        "category",
        "product",
        "seller",
        "quantity",
        "unit_price",
        "unit_cost",
    ]
    missing_values = int(sales[required_for_row].isna().sum().sum())
    if missing_values:
        warnings.append(f"{missing_values} valores obrigatórios inválidos foram encontrados.")

    valid_mask = (
        sales[required_for_row].notna().all(axis=1)
        & (sales["quantity"] > 0)
        & (sales["unit_price"] >= 0)
        & (sales["unit_cost"] >= 0)
    )
    sales = sales.loc[valid_mask].copy()

    sales["quantity"] = sales["quantity"].astype("int64")
    sales["revenue"] = sales["quantity"] * sales["unit_price"]
    sales["cost"] = sales["quantity"] * sales["unit_cost"]
    sales["profit"] = sales["revenue"] - sales["cost"]
    sales["margin_pct"] = np.where(
        sales["revenue"].ne(0), sales["profit"] / sales["revenue"] * 100, 0.0
    )
    sales["month"] = sales["sale_date"].dt.to_period("M").dt.to_timestamp()
    sales["year"] = sales["sale_date"].dt.year
    sales["month_number"] = sales["sale_date"].dt.month

    duplicate_orders = int(sales.duplicated(subset=["order_id"], keep=False).sum())
    if duplicate_orders:
        warnings.append(
            f"{duplicate_orders} linhas compartilham identificadores de pedido. "
            "Isso pode ser válido quando um pedido possui mais de um item."
        )

    sales = sales.sort_values(["sale_date", "order_id"]).reset_index(drop=True)
    removed_rows = original_rows - len(sales)
    if removed_rows:
        warnings.append(f"{removed_rows} linhas inválidas foram removidas.")

    report = DataQualityReport(
        original_rows=original_rows,
        valid_rows=len(sales),
        removed_rows=removed_rows,
        duplicate_orders=duplicate_orders,
        missing_values=missing_values,
        warnings=tuple(warnings),
    )
    return sales, report
