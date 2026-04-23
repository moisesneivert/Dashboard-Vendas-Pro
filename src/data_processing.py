from pathlib import Path
from typing import Iterable

import pandas as pd


COLUNAS_OBRIGATORIAS = {
    "data",
    "pedido_id",
    "cliente",
    "cidade",
    "estado",
    "regiao",
    "produto",
    "categoria",
    "vendedor",
    "canal_venda",
    "quantidade",
    "preco_unitario",
    "custo_unitario",
    "status_pagamento",
}

UFS_VALIDAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    dados = df.copy()
    dados.columns = [str(col).strip().lower() for col in dados.columns]
    return dados


def validate_required_columns(df: pd.DataFrame) -> None:
    faltantes = COLUNAS_OBRIGATORIAS - set(df.columns)
    if faltantes:
        raise ValueError(
            "A base não possui as seguintes colunas obrigatórias: "
            + ", ".join(sorted(faltantes))
        )


def clean_states(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    dados = df.copy()

    dados["estado"] = dados["estado"].astype(str).str.strip().str.upper()
    dados.loc[dados["estado"] == "RP", "estado"] = "PR"

    estados_invalidos = sorted(set(dados["estado"].dropna()) - UFS_VALIDAS)
    dados = dados[dados["estado"].isin(UFS_VALIDAS)].copy()

    return dados, estados_invalidos


def prepare_sales_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    dados = normalize_columns(df)
    validate_required_columns(dados)

    dados["data"] = pd.to_datetime(dados["data"], errors="coerce")
    dados["quantidade"] = pd.to_numeric(dados["quantidade"], errors="coerce").fillna(0)
    dados["preco_unitario"] = pd.to_numeric(dados["preco_unitario"], errors="coerce").fillna(0)
    dados["custo_unitario"] = pd.to_numeric(dados["custo_unitario"], errors="coerce").fillna(0)

    dados = dados.dropna(subset=["data"]).copy()
    dados, estados_invalidos = clean_states(dados)

    dados["faturamento"] = dados["quantidade"] * dados["preco_unitario"]
    dados["custo_total"] = dados["quantidade"] * dados["custo_unitario"]
    dados["lucro"] = dados["faturamento"] - dados["custo_total"]
    dados["margem_percentual"] = dados.apply(
        lambda linha: (linha["lucro"] / linha["faturamento"] * 100)
        if linha["faturamento"] > 0
        else 0,
        axis=1,
    )
    dados["mes"] = dados["data"].dt.to_period("M").dt.to_timestamp()

    return dados, estados_invalidos


def load_csv(path_or_file) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(path_or_file)
    return prepare_sales_data(df)


def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("mes", as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum"),
            pedidos=("pedido_id", "nunique"),
            quantidade=("quantidade", "sum"),
        )
        .sort_values("mes")
    )


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(value: float) -> str:
    return f"{value:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")