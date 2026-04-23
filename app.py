from pathlib import Path
import io

import pandas as pd
import streamlit as st

from src.auth import get_users_from_secrets, verify_password
from src.data_processing import (
    format_currency,
    format_percent,
    load_csv,
    prepare_sales_data,
)
from src.database import get_database_url, read_sales_from_postgres
from src.forecasting import forecast_monthly_sales
from src.goals import analyze_goals, load_goals


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


st.set_page_config(
    page_title="Dashboard Pro de Vendas",
    page_icon="📊",
    layout="wide",
)


def login_screen() -> None:
    st.title("Dashboard Pro de Vendas")
    st.caption("Entre para acessar o painel comercial.")

    users = get_users_from_secrets(st.secrets)

    if not users:
        st.error(
            "Nenhum usuário configurado. "
            "Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` "
            "e configure os usuários."
        )
        st.stop()

    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        user = users.get(username)

        if user and verify_password(password, user.get("password_hash", "")):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["name"] = user.get("name", username)
            st.session_state["role"] = user.get("role", "viewer")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")


def logout_button() -> None:
    with st.sidebar:
        st.caption(f"Logado como: **{st.session_state.get('name')}**")

        if st.button("Sair"):
            st.session_state.clear()
            st.rerun()


@st.cache_data
def load_default_sales():
    return load_csv(DATA_DIR / "vendas_exemplo.csv")


@st.cache_data
def load_uploaded_sales(file):
    return load_csv(file)


@st.cache_data
def load_postgres_sales(database_url: str):
    return read_sales_from_postgres(database_url)


def load_sales_source() -> tuple[pd.DataFrame, list[str], str]:
    st.sidebar.header("Fonte de dados")

    source = st.sidebar.radio(
        "Escolha a origem",
        ["Base exemplo", "Upload CSV", "PostgreSQL"],
    )

    if source == "Upload CSV":
        uploaded = st.sidebar.file_uploader("Envie o CSV de vendas", type=["csv"])

        if uploaded is None:
            st.info("Envie um CSV ou selecione outra fonte de dados.")
            st.stop()

        sales, invalid_states = load_uploaded_sales(uploaded)
        return sales, invalid_states, "Upload CSV"

    if source == "PostgreSQL":
        database_url = get_database_url(st.secrets)

        if not database_url:
            st.error(
                "URL do PostgreSQL não configurada em `.streamlit/secrets.toml` "
                "na chave `[connections.postgres] url`."
            )
            st.stop()

        sales, invalid_states = load_postgres_sales(database_url)

        if sales.empty:
            st.warning("A tabela `vendas` existe, mas ainda não possui registros.")
            st.stop()

        return sales, invalid_states, "PostgreSQL"

    sales, invalid_states = load_default_sales()
    return sales, invalid_states, "Base exemplo"


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")

    filtered = df.copy()

    period_min = filtered["data"].min().date()
    period_max = filtered["data"].max().date()

    period = st.sidebar.date_input(
        "Período",
        value=(period_min, period_max),
        min_value=period_min,
        max_value=period_max,
    )

    if len(period) == 2:
        start, end = period

        filtered = filtered[
            (filtered["data"].dt.date >= start)
            & (filtered["data"].dt.date <= end)
        ]

    filters = {
        "regiao": "Região",
        "estado": "Estado",
        "categoria": "Categoria",
        "produto": "Produto",
        "vendedor": "Vendedor",
        "canal_venda": "Canal de venda",
        "status_pagamento": "Status de pagamento",
    }

    for column, label in filters.items():
        options = sorted(filtered[column].dropna().unique())
        selected = st.sidebar.multiselect(label, options)

        if selected:
            filtered = filtered[filtered[column].isin(selected)]

    return filtered


def show_kpis(df: pd.DataFrame) -> None:
    revenue = df["faturamento"].sum()
    profit = df["lucro"].sum()
    orders = df["pedido_id"].nunique()
    quantity = df["quantidade"].sum()

    avg_ticket = revenue / orders if orders else 0
    margin = profit / revenue * 100 if revenue else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Faturamento", format_currency(revenue))
    col2.metric("Lucro", format_currency(profit))
    col3.metric("Pedidos", f"{orders:,}".replace(",", "."))
    col4.metric("Ticket médio", format_currency(avg_ticket))
    col5.metric("Margem", format_percent(margin))


def show_charts(df: pd.DataFrame) -> None:
    st.subheader("Análise visual")

    col1, col2 = st.columns(2)

    revenue_month = (
        df.groupby("mes", as_index=False)["faturamento"]
        .sum()
        .sort_values("mes")
        .set_index("mes")
    )

    category = (
        df.groupby("categoria", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
        .set_index("categoria")
    )

    with col1:
        st.markdown("**Faturamento por mês**")
        st.line_chart(revenue_month)

    with col2:
        st.markdown("**Faturamento por categoria**")
        st.bar_chart(category)

    col3, col4 = st.columns(2)

    top_products = (
        df.groupby("produto", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
        .head(10)
        .set_index("produto")
    )

    sellers = (
        df.groupby("vendedor", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
        .set_index("vendedor")
    )

    with col3:
        st.markdown("**Top 10 produtos por faturamento**")
        st.bar_chart(top_products)

    with col4:
        st.markdown("**Faturamento por vendedor**")
        st.bar_chart(sellers)


def show_goals(df: pd.DataFrame) -> None:
    st.subheader("Análise de metas")

    goals_file = st.file_uploader(
        "Opcional: envie um CSV de metas",
        type=["csv"],
        key="goals_upload",
        help="Colunas esperadas: mes, meta_faturamento, meta_lucro. Exemplo de mês: 2026-01.",
    )

    try:
        if goals_file is not None:
            goals = load_goals(goals_file)
        else:
            goals = load_goals(DATA_DIR / "metas_vendas.csv")

        goals_analysis = analyze_goals(df, goals)

        col1, col2 = st.columns(2)

        with col1:
            chart_df = goals_analysis[
                ["mes", "faturamento", "meta_faturamento"]
            ].set_index("mes")
            st.markdown("**Faturamento realizado x meta**")
            st.line_chart(chart_df)

        with col2:
            chart_df = goals_analysis[["mes", "lucro", "meta_lucro"]].set_index("mes")
            st.markdown("**Lucro realizado x meta**")
            st.line_chart(chart_df)

        st.dataframe(goals_analysis, width="stretch", hide_index=True)

    except Exception as exc:
        st.error(f"Erro na análise de metas: {exc}")


def show_forecast(df: pd.DataFrame) -> None:
    st.subheader("Previsão de vendas")

    months = st.slider("Meses à frente", min_value=1, max_value=12, value=3)

    try:
        forecast = forecast_monthly_sales(df, months_ahead=months)

        historical = (
            df.groupby("mes", as_index=False)
            .agg(faturamento=("faturamento", "sum"))
            .sort_values("mes")
        )

        historical["tipo"] = "Realizado"
        historical = historical.rename(columns={"faturamento": "valor"})

        forecast_chart = forecast.rename(columns={"faturamento_previsto": "valor"})
        forecast_chart["tipo"] = "Previsto"

        combined = pd.concat(
            [
                historical[["mes", "valor", "tipo"]],
                forecast_chart[["mes", "valor", "tipo"]],
            ],
            ignore_index=True,
        )

        pivot = combined.pivot_table(
            index="mes",
            columns="tipo",
            values="valor",
            aggfunc="sum",
        )

        st.line_chart(pivot)
        st.dataframe(forecast, width="stretch", hide_index=True)

        st.caption(
            "Modelo usado: regressão linear simples sobre o faturamento mensal. "
            "É uma previsão inicial para portfólio; em produção, valide sazonalidade, "
            "outliers e erro do modelo."
        )

    except Exception as exc:
        st.warning(f"Não foi possível gerar previsão: {exc}")


def show_tables(df: pd.DataFrame) -> None:
    st.subheader("Tabelas analíticas")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Resumo por produto",
            "Resumo por vendedor",
            "Resumo por região",
            "Base filtrada",
        ]
    )

    with tab1:
        summary_product = (
            df.groupby(["categoria", "produto"], as_index=False)
            .agg(
                quantidade_vendida=("quantidade", "sum"),
                faturamento=("faturamento", "sum"),
                lucro=("lucro", "sum"),
                margem_media=("margem_percentual", "mean"),
            )
            .sort_values("faturamento", ascending=False)
        )

        st.dataframe(summary_product, width="stretch", hide_index=True)

    with tab2:
        summary_seller = (
            df.groupby("vendedor", as_index=False)
            .agg(
                pedidos=("pedido_id", "nunique"),
                quantidade_vendida=("quantidade", "sum"),
                faturamento=("faturamento", "sum"),
                lucro=("lucro", "sum"),
            )
            .sort_values("faturamento", ascending=False)
        )

        st.dataframe(summary_seller, width="stretch", hide_index=True)

    with tab3:
        summary_region = (
            df.groupby(["regiao", "estado"], as_index=False)
            .agg(
                pedidos=("pedido_id", "nunique"),
                faturamento=("faturamento", "sum"),
                lucro=("lucro", "sum"),
            )
            .sort_values("faturamento", ascending=False)
        )

        st.dataframe(summary_region, width="stretch", hide_index=True)

    with tab4:
        st.dataframe(
            df.sort_values("data", ascending=False),
            width="stretch",
            hide_index=True,
        )

        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")

        st.download_button(
            label="Baixar base filtrada em CSV",
            data=buffer.getvalue(),
            file_name="base_filtrada_vendas.csv",
            mime="text/csv",
        )


def main() -> None:
    if not st.session_state.get("authenticated"):
        login_screen()
        return

    logout_button()

    st.title("Dashboard Pro de Vendas com Python")
    st.caption(
        "Pandas + Streamlit + autenticação + PostgreSQL + metas + previsão + testes."
    )

    sales, invalid_states, source_name = load_sales_source()

    if invalid_states:
        st.warning(
            "Estados inválidos encontrados e removidos da base: "
            + ", ".join(invalid_states)
        )

    filtered = sidebar_filters(sales)

    if filtered.empty:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")
        st.stop()

    st.info(f"Fonte de dados ativa: **{source_name}**")

    show_kpis(filtered)

    st.divider()

    show_charts(filtered)

    st.divider()

    tab_goals, tab_forecast, tab_tables = st.tabs(
        ["Metas", "Previsão de vendas", "Tabelas"]
    )

    with tab_goals:
        show_goals(filtered)

    with tab_forecast:
        show_forecast(filtered)

    with tab_tables:
        show_tables(filtered)


if __name__ == "__main__":
    main()