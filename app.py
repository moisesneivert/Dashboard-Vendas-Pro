import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.auth import get_users_from_secrets, verify_password
from src.data_processing import (
    format_currency,
    format_percent,
    load_csv,
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
def load_default_sales() -> tuple[pd.DataFrame, list[str]]:
    return load_csv(DATA_DIR / "vendas_exemplo.csv")


@st.cache_data
def load_uploaded_sales(file) -> tuple[pd.DataFrame, list[str]]:
    return load_csv(file)


@st.cache_data
def load_postgres_sales(database_url: str) -> tuple[pd.DataFrame, list[str]]:
    return read_sales_from_postgres(database_url)


def load_sales_source() -> tuple[pd.DataFrame, list[str], str]:
    st.sidebar.header("Fonte de dados")

    source = st.sidebar.radio(
        "Escolha a origem",
        ["Base exemplo", "Upload CSV", "PostgreSQL"],
    )

    try:
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

    except Exception as exc:
        st.error(f"Erro ao carregar dados: {exc}")
        st.stop()


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
        if column in filtered.columns:
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

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Faturamento", format_currency(revenue))
    col2.metric("Lucro", format_currency(profit))
    col3.metric("Pedidos", f"{orders:,}".replace(",", "."))
    col4.metric("Itens vendidos", f"{quantity:,}".replace(",", "."))
    col5.metric("Ticket médio", format_currency(avg_ticket))
    col6.metric("Margem", format_percent(margin))


def show_automatic_insights(df: pd.DataFrame) -> None:
    st.subheader("Insights automáticos")

    revenue = df["faturamento"].sum()
    profit = df["lucro"].sum()
    orders = df["pedido_id"].nunique()

    margin = profit / revenue * 100 if revenue else 0
    avg_ticket = revenue / orders if orders else 0

    best_category = (
        df.groupby("categoria")["faturamento"]
        .sum()
        .sort_values(ascending=False)
        .head(1)
    )

    best_seller = (
        df.groupby("vendedor")["faturamento"]
        .sum()
        .sort_values(ascending=False)
        .head(1)
    )

    best_product = (
        df.groupby("produto")["faturamento"]
        .sum()
        .sort_values(ascending=False)
        .head(1)
    )

    monthly_revenue = df.groupby("mes")["faturamento"].sum().sort_index()

    col1, col2 = st.columns(2)

    with col1:
        if not best_category.empty:
            st.success(
                f"Categoria destaque: **{best_category.index[0]}**, "
                f"com {format_currency(best_category.iloc[0])} em faturamento."
            )

        if not best_seller.empty:
            st.info(
                f"Vendedor com maior faturamento: **{best_seller.index[0]}**, "
                f"com {format_currency(best_seller.iloc[0])}."
            )

        if not best_product.empty:
            st.info(
                f"Produto mais forte: **{best_product.index[0]}**, "
                f"gerando {format_currency(best_product.iloc[0])}."
            )

    with col2:
        if margin < 10:
            st.warning(
                f"Margem baixa: **{format_percent(margin)}**. "
                "Avalie custos, descontos e precificação."
            )
        elif margin >= 25:
            st.success(
                f"Margem saudável: **{format_percent(margin)}**. "
                "O negócio apresenta boa rentabilidade."
            )
        else:
            st.info(
                f"Margem intermediária: **{format_percent(margin)}**. "
                "Há espaço para otimização."
            )

        st.info(f"Ticket médio atual: **{format_currency(avg_ticket)}** por pedido.")

        if len(monthly_revenue) >= 2:
            last_month = monthly_revenue.iloc[-1]
            previous_month = monthly_revenue.iloc[-2]

            variation = (
                (last_month - previous_month) / previous_month * 100
                if previous_month
                else 0
            )

            if variation > 0:
                st.success(
                    f"O faturamento cresceu **{format_percent(variation)}** "
                    "em relação ao mês anterior."
                )
            elif variation < 0:
                st.warning(
                    f"O faturamento caiu **{format_percent(abs(variation))}** "
                    "em relação ao mês anterior."
                )
            else:
                st.info("O faturamento ficou estável em relação ao mês anterior.")


def show_charts(df: pd.DataFrame) -> None:
    st.subheader("Análise visual")

    color_sequence = ["#D4AF37", "#111111", "#666666", "#B8860B"]

    revenue_month = (
        df.groupby("mes", as_index=False)["faturamento"]
        .sum()
        .sort_values("mes")
    )

    fig_month = px.line(
        revenue_month,
        x="mes",
        y="faturamento",
        markers=True,
        title="Faturamento por mês",
        color_discrete_sequence=["#D4AF37"],
    )

    fig_month.update_traces(line=dict(width=4))

    fig_month.update_layout(
        template="plotly_white",
        yaxis_title="Faturamento",
        xaxis_title="Mês",
        title_font_size=20,
        height=420,
    )

    category = (
        df.groupby("categoria", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
    )

    fig_category = px.bar(
        category,
        x="categoria",
        y="faturamento",
        title="Faturamento por categoria",
        color="categoria",
        color_discrete_sequence=color_sequence,
    )

    fig_category.update_layout(
        template="plotly_white",
        yaxis_title="Faturamento",
        xaxis_title="Categoria",
        showlegend=False,
        height=420,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_month, use_container_width=True)

    with col2:
        st.plotly_chart(fig_category, use_container_width=True)

    top_products = (
        df.groupby("produto", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
        .head(10)
    )

    fig_products = px.bar(
        top_products,
        x="faturamento",
        y="produto",
        orientation="h",
        title="Top 10 produtos por faturamento",
        color="faturamento",
        color_continuous_scale="Sunsetdark",
    )

    fig_products.update_layout(
        template="plotly_white",
        xaxis_title="Faturamento",
        yaxis_title="Produto",
        height=500,
    )

    fig_products.update_yaxes(categoryorder="total ascending")

    sellers = (
        df.groupby("vendedor", as_index=False)["faturamento"]
        .sum()
        .sort_values("faturamento", ascending=False)
    )

    fig_sellers = px.bar(
        sellers,
        x="vendedor",
        y="faturamento",
        title="Faturamento por vendedor",
        color="faturamento",
        color_continuous_scale="Cividis",
    )

    fig_sellers.update_layout(
        template="plotly_white",
        yaxis_title="Faturamento",
        xaxis_title="Vendedor",
        height=500,
    )

    col3, col4 = st.columns(2)

    with col3:
        st.plotly_chart(fig_products, use_container_width=True)

    with col4:
        st.plotly_chart(fig_sellers, use_container_width=True)


def show_goals(df: pd.DataFrame) -> None:
    st.subheader("Análise de metas")

    goals_file = st.file_uploader(
        "Opcional: envie um CSV de metas",
        type=["csv"],
        key="goals_upload",
        help=(
            "Colunas esperadas: mes, meta_faturamento, meta_lucro. "
            "Exemplo de mês: 2026-01."
        ),
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

            fig_goal_revenue = px.line(
                chart_df,
                markers=True,
                title="Faturamento realizado x meta",
            )

            fig_goal_revenue.update_layout(
                template="plotly_white",
                yaxis_title="Valor",
                xaxis_title="Mês",
                height=420,
            )

            st.plotly_chart(fig_goal_revenue, use_container_width=True)

        with col2:
            chart_df = goals_analysis[["mes", "lucro", "meta_lucro"]].set_index("mes")

            fig_goal_profit = px.line(
                chart_df,
                markers=True,
                title="Lucro realizado x meta",
            )

            fig_goal_profit.update_layout(
                template="plotly_white",
                yaxis_title="Valor",
                xaxis_title="Mês",
                height=420,
            )

            st.plotly_chart(fig_goal_profit, use_container_width=True)

        st.dataframe(goals_analysis, use_container_width=True, hide_index=True)

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

        fig_forecast = px.line(
            combined,
            x="mes",
            y="valor",
            color="tipo",
            markers=True,
            title="Faturamento realizado x previsto",
            color_discrete_sequence=["#111111", "#D4AF37"],
        )

        fig_forecast.update_traces(line=dict(width=4))

        fig_forecast.update_layout(
            template="plotly_white",
            yaxis_title="Faturamento",
            xaxis_title="Mês",
            height=450,
        )

        st.plotly_chart(fig_forecast, use_container_width=True)
        st.dataframe(forecast, use_container_width=True, hide_index=True)

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

        st.dataframe(summary_product, use_container_width=True, hide_index=True)

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

        st.dataframe(summary_seller, use_container_width=True, hide_index=True)

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

        st.dataframe(summary_region, use_container_width=True, hide_index=True)

    with tab4:
        st.dataframe(
            df.sort_values("data", ascending=False),
            use_container_width=True,
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

    show_automatic_insights(filtered)

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
