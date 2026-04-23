# Dashboard Vendas Pro

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Forecasting-orange)
![Pytest](https://img.shields.io/badge/Pytest-Tests-green)
![Status](https://img.shields.io/badge/Status-Portfolio%20Project-success)

Dashboard profissional de vendas desenvolvido com **Python, Pandas e Streamlit**, com **autenticação de usuários**, **análise de metas**, **previsão de vendas**, **integração com PostgreSQL** e **testes automatizados**.

## Visão geral

Este projeto foi construído como uma aplicação prática de análise comercial, com foco em cenários reais de negócio e boas práticas de desenvolvimento em Python.

A proposta é transformar uma base de vendas em um painel interativo, permitindo:

- acompanhar indicadores de desempenho;
- aplicar filtros dinâmicos;
- comparar resultados com metas mensais;
- visualizar tendências de faturamento;
- gerar previsões de vendas;
- trabalhar com arquivos CSV ou banco PostgreSQL.

## Demonstração

### Principais recursos

- Autenticação com login
- Base local de exemplo
- Upload de CSV
- Integração com PostgreSQL
- KPIs comerciais
- Filtros por período e dimensões de negócio
- Gráficos interativos
- Análise de metas mensais
- Previsão de vendas
- Exportação da base filtrada
- Testes automatizados com Pytest

## Stack utilizada

- **Python**
- **Pandas**
- **Streamlit**
- **PostgreSQL**
- **SQLAlchemy**
- **Scikit-learn**
- **Pytest**

## Funcionalidades

### 1. Autenticação de usuários
O sistema possui tela de login com validação de credenciais via arquivo de secrets.

### 2. Fonte de dados flexível
A aplicação permite usar três fontes:

- base local de exemplo;
- upload manual de CSV;
- leitura de dados a partir do PostgreSQL.

### 3. KPIs comerciais
O dashboard calcula automaticamente:

- faturamento total;
- lucro total;
- quantidade vendida;
- número de pedidos;
- ticket médio;
- margem percentual.

### 4. Filtros interativos
É possível filtrar os dados por:

- período;
- região;
- estado;
- categoria;
- produto;
- vendedor;
- canal de venda;
- status de pagamento.

### 5. Visualização analítica
O painel apresenta gráficos de:

- faturamento por mês;
- faturamento por categoria;
- top 10 produtos;
- faturamento por vendedor;
- faturamento por região;
- faturamento por canal.

### 6. Análise de metas
A aplicação compara o realizado com metas mensais de faturamento e lucro, exibindo:

- valor realizado;
- valor da meta;
- percentual de atingimento;
- status da meta.

### 7. Previsão de vendas
Foi implementada uma previsão inicial de faturamento com regressão linear simples usando `scikit-learn`.

### 8. Testes automatizados
O projeto conta com testes unitários para validar:

- autenticação;
- tratamento dos dados;
- limpeza de estados inválidos;
- análise de metas;
- geração de previsões.

## Estrutura do projeto

```bash
dashboard-vendas-pro/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
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
