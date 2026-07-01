from __future__ import annotations

from io import BytesIO, StringIO
from pathlib import Path
from typing import BinaryIO, TextIO

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from .exceptions import DataSourceError


def load_csv(
    source: str | Path | BinaryIO | TextIO | BytesIO | StringIO,
) -> pd.DataFrame:
    """Carrega um arquivo CSV e retorna os dados em um DataFrame.

    Args:
        source: Caminho, arquivo ou objeto em memória contendo o CSV.

    Returns:
        DataFrame com os dados carregados.

    Raises:
        DataSourceError: Quando o arquivo não pode ser lido ou possui
        conteúdo inválido.
    """
    try:
        return pd.read_csv(source)
    except (
        OSError,
        UnicodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        ValueError,
    ) as exc:
        raise DataSourceError(f"Não foi possível ler o arquivo CSV: {exc}") from exc


def load_sales_from_database(
    database_url: str,
    query: str,
) -> pd.DataFrame:
    """Carrega dados de vendas de um banco SQL.

    Apenas consultas iniciadas com SELECT são permitidas.

    Args:
        database_url: URL de conexão compatível com SQLAlchemy.
        query: Consulta SELECT utilizada para carregar os dados.

    Returns:
        DataFrame com o resultado da consulta.

    Raises:
        DataSourceError: Quando a configuração é inválida ou ocorre
        alguma falha na consulta.
    """
    if not database_url or not database_url.strip():
        raise DataSourceError("A URL do banco de dados não foi informada.")

    normalized_query = query.strip()

    if not normalized_query:
        raise DataSourceError("A consulta ao banco de dados não foi informada.")

    if not normalized_query.lower().startswith("select"):
        raise DataSourceError("Somente consultas SELECT são permitidas.")

    engine = None

    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
        )

        with engine.connect() as connection:
            return pd.read_sql_query(
                text(normalized_query),
                connection,
            )

    except (SQLAlchemyError, pd.errors.DatabaseError) as exc:
        raise DataSourceError(f"Falha ao consultar o banco de dados: {exc}") from exc

    finally:
        if engine is not None:
            engine.dispose()
