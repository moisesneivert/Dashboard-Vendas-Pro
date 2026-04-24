# Dashboard de Vendas Pro

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Pandas](https://img.shields.io/badge/Pandas-An%C3%A1lise%20de%20Dados-green)
![Plotly](https://img.shields.io/badge/Plotly-Gr%C3%A1ficos%20Interativos-purple)
![Pytest](https://img.shields.io/badge/Pytest-Testes-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Dashboard profissional de vendas desenvolvido com **Python**, **Streamlit**, **Pandas** e **Plotly**, com foco em análise comercial, indicadores de desempenho, visualização interativa de dados, autenticação de usuários, metas, previsão de vendas e integração com PostgreSQL.

Este projeto foi criado como parte do meu portfólio para demonstrar habilidades práticas em desenvolvimento Python, análise de dados, organização de código, testes automatizados e construção de aplicações web com Streamlit.

---

## Acesse o projeto online

[Dashboard publicado no Streamlit Community Cloud](https://dashboard-vendas-pro-zaj5qlcnq25abddvpqkcxz.streamlit.app/)

---

## Funcionalidades

- Autenticação de usuários com `st.secrets`
- Dashboard interativo desenvolvido com Streamlit
- Carregamento de dados por três fontes:
  - Base exemplo
  - Upload de CSV
  - PostgreSQL
- KPIs comerciais:
  - Faturamento
  - Lucro
  - Pedidos
  - Itens vendidos
  - Ticket médio
  - Margem
- Filtros dinâmicos por:
  - Período
  - Região
  - Estado
  - Categoria
  - Produto
  - Vendedor
  - Canal de venda
  - Status de pagamento
- Insights automáticos sobre categoria, vendedor, produto, margem e variação mensal
- Gráficos interativos com Plotly
- Análise de metas de faturamento e lucro
- Previsão simples de vendas com regressão linear
- Tabelas analíticas por produto, vendedor e região
- Exportação da base filtrada em CSV
- Estrutura modular em Python
- Testes automatizados com Pytest

---

## Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- Scikit-learn
- SQLAlchemy
- PostgreSQL
- Pytest

---

## Estrutura do projeto

```text
Dashboard-Vendas-Pro/
├── app.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── .streamlit/
│   └── secrets.toml.example
│
├── data/
│   ├── vendas_exemplo.csv
│   └── metas_vendas.csv
│
├── sql/
│   └── schema.sql
│
├── src/
│   ├── auth.py
│   ├── database.py
│   ├── data_processing.py
│   ├── forecasting.py
│   └── goals.py
│
└── tests/
    ├── test_auth.py
    ├── test_data_processing.py
    ├── test_forecasting.py
    └── test_goals.py
