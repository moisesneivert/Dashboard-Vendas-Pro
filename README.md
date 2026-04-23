# Dashboard Pro de Vendas com Python

Projeto de portfólio para Python, dados e backend leve com Streamlit.

## Funcionalidades implementadas

- Autenticação de usuário com senha protegida por hash PBKDF2.
- Conexão opcional com PostgreSQL.
- Upload de CSV.
- Base de vendas exemplo.
- Validação e limpeza de estados inválidos.
- KPIs comerciais.
- Gráficos de faturamento, categoria, produto e vendedor.
- Análise de metas mensais.
- Previsão de vendas com regressão linear.
- Exportação de base filtrada.
- Testes automatizados com Pytest.
- Estrutura pronta para deploy no Streamlit Community Cloud.

## Usuários locais de teste

Configure o arquivo `.streamlit/secrets.toml`.

Copie:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Usuários de teste:

```text
admin / admin123
analista / dados123
```

Troque essas credenciais antes de publicar.

## Como rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Como rodar os testes

```bash
pytest
```

## PostgreSQL

O app pode usar PostgreSQL como fonte de dados.

No arquivo `.streamlit/secrets.toml`, configure:

```toml
[connections.postgres]
url = "postgresql+psycopg://usuario:senha@host:5432/database"
```

Para banco com SSL, use:

```toml
url = "postgresql+psycopg://usuario:senha@host:5432/database?sslmode=require"
```

Crie a tabela usando:

```bash
psql "sua_url_do_banco" -f sql/schema.sql
```

## Formato do CSV de vendas

A base deve conter:

```text
data
pedido_id
cliente
cidade
estado
regiao
produto
categoria
vendedor
canal_venda
quantidade
preco_unitario
custo_unitario
status_pagamento
```

## Formato do CSV de metas

A base deve conter:

```text
mes
meta_faturamento
meta_lucro
```

Exemplo:

```text
2026-01,500000,130000
2026-02,550000,145000
```

## Estrutura

```text
dashboard_vendas_streamlit_pro/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── data/
│   ├── vendas_exemplo.csv
│   └── metas_vendas.csv
├── sql/
│   └── schema.sql
├── src/
│   ├── auth.py
│   ├── data_processing.py
│   ├── database.py
│   ├── forecasting.py
│   └── goals.py
└── tests/
    ├── test_auth.py
    ├── test_data_processing.py
    ├── test_forecasting.py
    └── test_goals.py
```
