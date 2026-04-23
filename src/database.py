from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text

from src.data_processing import prepare_sales_data


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS vendas (
    data DATE NOT NULL,
    pedido_id TEXT PRIMARY KEY,
    cliente TEXT,
    cidade TEXT,
    estado TEXT,
    regiao TEXT,
    produto TEXT,
    categoria TEXT,
    vendedor TEXT,
    canal_venda TEXT,
    quantidade INTEGER,
    preco_unitario NUMERIC(12, 2),
    custo_unitario NUMERIC(12, 2),
    status_pagamento TEXT
);
"""


def get_database_url(st_secrets: Any) -> str | None:
    try:
        return st_secrets["connections"]["postgres"]["url"]
    except Exception:
        return None


def create_db_engine(database_url: str):
    return create_engine(database_url, pool_pre_ping=True)


def read_sales_from_postgres(database_url: str) -> tuple[pd.DataFrame, list[str]]:
    engine = create_db_engine(database_url)

    with engine.begin() as conn:
        conn.execute(text(CREATE_TABLE_SQL))

    query = """
    SELECT
        data,
        pedido_id,
        cliente,
        cidade,
        estado,
        regiao,
        produto,
        categoria,
        vendedor,
        canal_venda,
        quantidade,
        preco_unitario,
        custo_unitario,
        status_pagamento
    FROM vendas
    ORDER BY data DESC;
    """

    df = pd.read_sql_query(query, engine)
    return prepare_sales_data(df)


def upsert_sales_to_postgres(database_url: str, df: pd.DataFrame) -> int:
    """
    Envia dados para PostgreSQL. Para simplificar o projeto de portfólio,
    faz append após garantir tabela. Use staging/upsert real em produção.
    """
    engine = create_db_engine(database_url)

    with engine.begin() as conn:
        conn.execute(text(CREATE_TABLE_SQL))

    expected_cols = [
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
    ]

    raw_df = df[expected_cols].copy()
    raw_df.to_sql("vendas", engine, if_exists="append", index=False, method="multi")
    return len(raw_df)