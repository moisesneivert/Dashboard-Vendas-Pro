# Dashboard de Vendas Pro

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Pandas](https://img.shields.io/badge/Pandas-An%C3%A1lise%20de%20Dados-green)
![Plotly](https://img.shields.io/badge/Plotly-Gr%C3%A1ficos%20Interativos-purple)
![Pytest](https://img.shields.io/badge/Pytest-Testes-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Dashboard profissional de vendas desenvolvido com **Python**, **Streamlit** e **Pandas**, com foco em análise comercial, indicadores de desempenho, visualização interativa de dados, autenticação de usuários, metas, previsão de vendas e integração com PostgreSQL.

Este projeto foi criado como parte do meu portfólio para demonstrar habilidades práticas em desenvolvimento Python, análise de dados, organização de código, testes automatizados e construção de aplicações web com Streamlit.

---

## Acesse o projeto online

[Dashboard publicado no Streamlit Community Cloud](https://dashboard-vendas-pro-zaj5qlcnq25abddvpqkcxz.streamlit.app/)

---

## Demonstração

### Visão geral do dashboard

![Visão geral do dashboard](assets/dashboard_overview.png)

### Gráficos e indicadores

![Gráficos do dashboard](assets/dashboard_charts.png)

### Tabelas analíticas

![Tabelas do dashboard](assets/dashboard_tables.png)

---

## Funcionalidades

- Autenticação de usuários via `st.secrets`
- Dashboard interativo com Streamlit
- KPIs comerciais:
  - Faturamento
  - Lucro
  - Pedidos
  - Ticket médio
  - Margem
- Filtros por:
  - Período
  - Região
  - Estado
  - Categoria
  - Produto
  - Vendedor
  - Canal de venda
  - Status de pagamento
- Gráficos interativos com Plotly
- Análise de faturamento por mês
- Análise por categoria, produto e vendedor
- Análise de metas de faturamento e lucro
- Previsão simples de vendas com Scikit-learn
- Upload de arquivo CSV
- Leitura de base exemplo
- Integração com PostgreSQL
- Exportação da base filtrada em CSV
- Testes automatizados com Pytest
- Estrutura modular em Python

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
├── app.py                  # Aplicação principal Streamlit
├── requirements.txt        # Dependências principais do projeto
├── README.md               # Documentação do projeto
├── LICENSE                 # Licença do projeto
├── .gitignore              # Arquivos ignorados pelo Git
│
├── assets/                 # Imagens utilizadas no README
│   ├── dashboard_overview.png
│   ├── dashboard_charts.png
│   └── dashboard_tables.png
│
├── data/                   # Bases de exemplo
│   ├── vendas_exemplo.csv
│   └── metas_vendas.csv
│
├── sql/                    # Scripts SQL
│   └── schema.sql
│
├── src/                    # Módulos da aplicação
│   ├── auth.py             # Autenticação e verificação de senha
│   ├── database.py         # Conexão com banco de dados
│   ├── data_processing.py  # Tratamento e preparação dos dados
│   ├── forecasting.py      # Previsão de vendas
│   └── goals.py            # Análise de metas
│
└── tests/                  # Testes automatizados
    ├── test_auth.py
    ├── test_data_processing.py
    ├── test_forecasting.py
    └── test_goals.py
