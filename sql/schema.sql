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

CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data);
CREATE INDEX IF NOT EXISTS idx_vendas_estado ON vendas(estado);
CREATE INDEX IF NOT EXISTS idx_vendas_categoria ON vendas(categoria);
CREATE INDEX IF NOT EXISTS idx_vendas_vendedor ON vendas(vendedor);