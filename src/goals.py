from pathlib import Path

import pandas as pd


def load_goals(path_or_file) -> pd.DataFrame:
    metas = pd.read_csv(path_or_file)
    metas.columns = [str(col).strip().lower() for col in metas.columns]

    required = {"mes", "meta_faturamento", "meta_lucro"}
    missing = required - set(metas.columns)
    if missing:
        raise ValueError(
            "Arquivo de metas inválido. Colunas obrigatórias: "
            + ", ".join(sorted(required))
        )

    metas["mes"] = pd.to_datetime(metas["mes"], format="%Y-%m", errors="coerce")
    metas["meta_faturamento"] = pd.to_numeric(metas["meta_faturamento"], errors="coerce").fillna(0)
    metas["meta_lucro"] = pd.to_numeric(metas["meta_lucro"], errors="coerce").fillna(0)

    return metas.dropna(subset=["mes"])


def analyze_goals(sales_df: pd.DataFrame, goals_df: pd.DataFrame) -> pd.DataFrame:
    realizado = (
        sales_df.groupby("mes", as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum"),
        )
    )

    analise = realizado.merge(goals_df, on="mes", how="left")

    analise["meta_faturamento"] = analise["meta_faturamento"].fillna(0)
    analise["meta_lucro"] = analise["meta_lucro"].fillna(0)

    analise["atingimento_faturamento_%"] = analise.apply(
        lambda row: (row["faturamento"] / row["meta_faturamento"] * 100)
        if row["meta_faturamento"] > 0
        else 0,
        axis=1,
    )

    analise["atingimento_lucro_%"] = analise.apply(
        lambda row: (row["lucro"] / row["meta_lucro"] * 100)
        if row["meta_lucro"] > 0
        else 0,
        axis=1,
    )

    analise["status_meta"] = analise["atingimento_faturamento_%"].apply(
        lambda x: "Atingida" if x >= 100 else "Abaixo da meta"
    )

    return analise.sort_values("mes")