from __future__ import annotations

SALES_COLUMNS = {
    "sale_date",
    "order_id",
    "region",
    "state",
    "category",
    "product",
    "seller",
    "channel",
    "payment_status",
    "quantity",
    "unit_price",
    "unit_cost",
}

COLUMN_ALIASES = {
    "data": "sale_date",
    "date": "sale_date",
    "pedido": "order_id",
    "id_pedido": "order_id",
    "regiao": "region",
    "região": "region",
    "estado": "state",
    "categoria": "category",
    "produto": "product",
    "vendedor": "seller",
    "canal": "channel",
    "status_pagamento": "payment_status",
    "quantidade": "quantity",
    "preco_unitario": "unit_price",
    "preço_unitário": "unit_price",
    "custo_unitario": "unit_cost",
    "custo_unitário": "unit_cost",
}

GOAL_COLUMNS = {"month", "revenue_goal", "profit_goal"}
GOAL_ALIASES = {
    "mes": "month",
    "mês": "month",
    "meta_faturamento": "revenue_goal",
    "meta_lucro": "profit_goal",
}
