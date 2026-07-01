from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from .auth import authenticate
from .charts import (
    channel_share,
    forecast_chart,
    goal_chart,
    margin_by_category,
    ranking_bar,
    revenue_profit_over_time,
)
from .config import AppSettings
from .data_processing import DataQualityReport, prepare_sales_data
from .data_sources import load_csv, load_sales_from_database
from .exceptions import DashboardError, ForecastError
from .filters import SalesFilters, apply_filters
from .forecasting import forecast_monthly_revenue
from .formatting import currency_brl, delta_percentage, integer_br, percentage_br
from .goals import calculate_goal_performance, prepare_goals
from .insights import generate_insights
from .metrics import calculate_kpis, latest_month_changes, monthly_summary


def _read_secret(path: tuple[str, ...], default=None):
    current = st.secrets
    try:
        for key in path:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def _users_from_config() -> list[dict]:
    configured = _read_secret(("auth", "users"), [])
    return [dict(user) for user in configured]


def _render_login() -> None:
    st.title("🔐 Dashboard de Vendas Pro")
    st.caption("Entre com uma conta configurada em `.streamlit/secrets.toml`.")
    with st.form("login", clear_on_submit=False):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar", width="stretch")
    if submitted:
        user = authenticate(username, password, _users_from_config())
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            st.rerun()
        st.error("Usuário ou senha inválidos.")


def _require_authentication() -> bool:
    if st.session_state.get("authenticated"):
        return True
    if not _users_from_config():
        st.error(
            "Nenhum usuário foi configurado. Copie `.streamlit/secrets.toml.example` "
            "para `.streamlit/secrets.toml`."
        )
        return False
    _render_login()
    return False


def _load_source(settings: AppSettings) -> tuple[pd.DataFrame, str]:
    st.sidebar.subheader("Fonte de dados")
    source = st.sidebar.radio("Origem", ["Base de exemplo", "Upload CSV", "PostgreSQL"])
    if source == "Base de exemplo":
        return load_csv(settings.sales_file), source
    if source == "Upload CSV":
        upload = st.sidebar.file_uploader("Selecione um CSV", type=["csv"])
        if upload is None:
            st.info("Envie um arquivo CSV para continuar.")
            st.stop()
        return load_csv(upload), source

    database_url = _read_secret(("database", "url"), None) or settings.database_url
    query = _read_secret(("database", "query"), settings.database_query)
    return load_sales_from_database(str(database_url or ""), str(query)), source


def _multiselect(label: str, frame: pd.DataFrame, column: str) -> tuple[str, ...]:
    options = sorted(frame[column].dropna().astype(str).unique().tolist())
    return tuple(st.sidebar.multiselect(label, options))


def _build_filters(frame: pd.DataFrame) -> SalesFilters:
    st.sidebar.subheader("Filtros")
    min_date = frame["sale_date"].min().date()
    max_date = frame["sale_date"].max().date()
    selected = st.sidebar.date_input(
        "Período", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if isinstance(selected, tuple) and len(selected) == 2:
        start_date, end_date = selected
    else:
        start_date = end_date = selected
    return SalesFilters(
        start_date=start_date,
        end_date=end_date,
        regions=_multiselect("Região", frame, "region"),
        states=_multiselect("Estado", frame, "state"),
        categories=_multiselect("Categoria", frame, "category"),
        products=_multiselect("Produto", frame, "product"),
        sellers=_multiselect("Vendedor", frame, "seller"),
        channels=_multiselect("Canal", frame, "channel"),
        payment_statuses=_multiselect("Pagamento", frame, "payment_status"),
    )


def _render_quality(report: DataQualityReport, source: str) -> None:
    with st.expander("Qualidade e origem dos dados"):
        st.write(f"**Origem:** {source}")
        cols = st.columns(4)
        cols[0].metric("Linhas recebidas", report.original_rows)
        cols[1].metric("Linhas válidas", report.valid_rows)
        cols[2].metric("Linhas removidas", report.removed_rows)
        cols[3].metric("Pedidos repetidos", report.duplicate_orders)
        for warning in report.warnings:
            st.warning(warning)


def _render_kpis(frame: pd.DataFrame) -> None:
    kpis = calculate_kpis(frame)
    changes = latest_month_changes(frame)
    columns = st.columns(6)
    columns[0].metric(
        "Faturamento", currency_brl(kpis.revenue), delta_percentage(changes["revenue"])
    )
    columns[1].metric("Lucro", currency_brl(kpis.profit), delta_percentage(changes["profit"]))
    columns[2].metric("Pedidos", integer_br(kpis.orders), delta_percentage(changes["orders"]))
    columns[3].metric("Itens", integer_br(kpis.items))
    columns[4].metric("Ticket médio", currency_brl(kpis.average_ticket))
    columns[5].metric("Margem", percentage_br(kpis.margin_pct))


def _render_overview(frame: pd.DataFrame) -> None:
    monthly = monthly_summary(frame)
    left, right = st.columns([2, 1])
    left.plotly_chart(revenue_profit_over_time(monthly), width="stretch")
    right.plotly_chart(channel_share(frame), width="stretch")
    left, right = st.columns(2)
    left.plotly_chart(ranking_bar(frame, "category", "Faturamento por categoria"), width="stretch")
    right.plotly_chart(ranking_bar(frame, "seller", "Ranking de vendedores"), width="stretch")
    st.plotly_chart(margin_by_category(frame), width="stretch")


def _render_goals(frame: pd.DataFrame, goals_file: Path) -> None:
    st.subheader("Metas comerciais")
    try:
        goals = prepare_goals(load_csv(goals_file))
        performance = calculate_goal_performance(monthly_summary(frame), goals)
        if performance["revenue_goal"].notna().sum() == 0:
            st.info("Não há metas cadastradas para o período filtrado.")
            return
        left, right = st.columns(2)
        left.plotly_chart(
            goal_chart(performance, "revenue", "revenue_goal", "Meta de faturamento"),
            width="stretch",
        )
        right.plotly_chart(
            goal_chart(performance, "profit", "profit_goal", "Meta de lucro"),
            width="stretch",
        )
        st.dataframe(
            performance[
                [
                    "month",
                    "revenue_achievement_pct",
                    "profit_achievement_pct",
                    "revenue_gap",
                    "profit_gap",
                ]
            ],
            width="stretch",
            hide_index=True,
        )
    except DashboardError as exc:
        st.warning(str(exc))


def _render_forecast(frame: pd.DataFrame) -> None:
    st.subheader("Previsão de faturamento")
    periods = st.slider("Meses projetados", min_value=1, max_value=12, value=3)
    try:
        forecast, model_metrics = forecast_monthly_revenue(frame, periods)
        st.plotly_chart(forecast_chart(forecast), width="stretch")
        cols = st.columns(3)
        cols[0].metric("MAE do ajuste", currency_brl(model_metrics["mae"]))
        cols[1].metric("R²", f"{model_metrics['r2']:.3f}")
        cols[2].metric("Tendência mensal", currency_brl(model_metrics["monthly_trend"]))
        st.caption(
            "Modelo demonstrativo de regressão linear. Não deve ser usado isoladamente para decisões financeiras."
        )
    except ForecastError as exc:
        st.info(str(exc))


def _render_tables(frame: pd.DataFrame) -> None:
    st.subheader("Análises detalhadas")
    dimension = st.selectbox(
        "Agrupar por", ["product", "seller", "region", "state", "category", "channel"]
    )
    table = (
        frame.groupby(dimension, as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
            items=("quantity", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )
    table["margin_pct"] = table["profit"].div(table["revenue"]).mul(100)
    st.dataframe(table, width="stretch", hide_index=True)


def _render_download(frame: pd.DataFrame) -> None:
    st.download_button(
        "Baixar dados filtrados em CSV",
        data=frame.to_csv(index=False).encode("utf-8-sig"),
        file_name="vendas_filtradas.csv",
        mime="text/csv",
    )


def run_dashboard() -> None:
    st.set_page_config(page_title="Dashboard de Vendas Pro", page_icon="📊", layout="wide")
    settings = AppSettings.from_environment()

    if not _require_authentication():
        return

    user = st.session_state["user"]
    with st.sidebar:
        st.success(f"Conectado como {user.name}")
        st.caption(f"Perfil: {user.role}")
        if st.button("Sair", width="stretch"):
            st.session_state.clear()
            st.rerun()

    st.title("📊 Dashboard de Vendas Pro")
    st.caption("Análise comercial, metas, qualidade de dados e previsão de faturamento.")

    try:
        raw, source = _load_source(settings)
        sales, report = prepare_sales_data(raw)
        filters = _build_filters(sales)
        filtered = apply_filters(sales, filters)
    except DashboardError as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error("Ocorreu um erro inesperado ao preparar o dashboard.")
        if os.getenv("DASHBOARD_DEBUG", "false").lower() == "true":
            st.exception(exc)
        return

    _render_quality(report, source)
    if filtered.empty:
        st.warning("Nenhuma venda corresponde aos filtros selecionados.")
        return

    _render_kpis(filtered)
    tabs = st.tabs(["Visão geral", "Insights", "Metas", "Previsão", "Tabelas"])
    with tabs[0]:
        _render_overview(filtered)
    with tabs[1]:
        st.subheader("Insights automáticos")
        for insight in generate_insights(filtered):
            st.markdown(f"- {insight}")
    with tabs[2]:
        _render_goals(filtered, settings.goals_file)
    with tabs[3]:
        _render_forecast(filtered)
    with tabs[4]:
        _render_tables(filtered)
        _render_download(filtered)
